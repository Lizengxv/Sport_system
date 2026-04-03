import io
import os
import random
from datetime import datetime
from typing import List, Optional, Dict

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, distinct

from .db import Base, engine, SessionLocal
from .models import (
    User,
    Athlete,
    Grouping,
    Event,
    Result,
    PersonalRanking,
    CollegeRanking,
)
from .schemas import (
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    AthleteCreate,
    AthleteUpdate,
    GroupGenerateRequest,
    GroupConfirmRequest,
    ResultSubmitRequest,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Sports Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MULTI_ROUND_EVENTS = {"100米", "200米", "400米", "4*100米"}
MIXED_EVENTS = {"4*200米", "混合4*100米"}
DISTANCE_KEYWORDS = {"跳", "掷", "远", "高", "铅球"}
LAST_IMPORT_TS = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def hash_password(plain):
    return pwd_context.hash(plain)


def is_distance_event(event_name: str) -> bool:
    return any(key in event_name for key in DISTANCE_KEYWORDS)


def sort_scores(scores: List[float], event_name: str):
    reverse = is_distance_event(event_name)
    return sorted(scores, reverse=reverse)


def rank_athletes_by_score(rows: List[Dict], event_name: str):
    reverse = is_distance_event(event_name)
    rows_sorted = sorted(rows, key=lambda r: r["score"], reverse=reverse)
    for idx, row in enumerate(rows_sorted, start=1):
        row["rank"] = idx
    return rows_sorted


def points_for_rank(rank: int) -> int:
    mapping = {1: 10, 2: 8, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
    return mapping.get(rank, 0)


def distribute_by_college(candidates: List[Athlete]) -> List[Athlete]:
    buckets: Dict[str, List[Athlete]] = {}
    for item in candidates:
        buckets.setdefault(item.college, []).append(item)
    for key in buckets:
        random.shuffle(buckets[key])
    ordered = []
    while any(buckets.values()):
        for college in list(buckets.keys()):
            if buckets[college]:
                ordered.append(buckets[college].pop())
    return ordered


def get_timestamp():
    global LAST_IMPORT_TS
    if LAST_IMPORT_TS:
        return LAST_IMPORT_TS
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


@app.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == req.email))
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        school=req.school,
        email=req.email,
        password_hash=hash_password(req.password),
        must_reset=False,
    )
    db.add(user)
    db.commit()
    return {"message": "registered"}


@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.school == req.school))
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "message": "ok",
        "school": user.school,
        "email": user.email,
        "must_reset": user.must_reset,
    }


@app.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == req.email))
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    user.password_hash = hash_password(req.new_password)
    user.must_reset = False
    db.commit()
    return {"message": "password updated"}


@app.get("/athletes")
def list_athletes(
    college: Optional[str] = None,
    name: Optional[str] = None,
    student_id: Optional[str] = None,
    gender: Optional[str] = None,
    event: Optional[str] = None,
    group_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(Athlete)
    if college:
        query = query.where(Athlete.college == college)
    if name:
        query = query.where(Athlete.name == name)
    if student_id:
        query = query.where(Athlete.student_id == student_id)
    if gender:
        query = query.where(Athlete.gender == gender)
    if event:
        query = query.where(Athlete.event == event)
    if group_name:
        query = query.where(Athlete.group_name == group_name)
    return [to_dict(row) for row in db.scalars(query).all()]


@app.post("/athletes")
def create_athlete(req: AthleteCreate, db: Session = Depends(get_db)):
    athlete = Athlete(**req.model_dump())
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return to_dict(athlete)


@app.put("/athletes/{athlete_id}")
def update_athlete(athlete_id: int, req: AthleteUpdate, db: Session = Depends(get_db)):
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in req.model_dump(exclude_unset=True).items():
        setattr(athlete, key, value)
    db.commit()
    return to_dict(athlete)


@app.delete("/athletes/{athlete_id}")
def delete_athlete(athlete_id: int, db: Session = Depends(get_db)):
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(athlete)
    db.commit()
    return {"message": "deleted"}


@app.post("/athletes/import")
def import_athletes(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_excel(file.file)
    expected = [
        "学院",
        "姓名",
        "学号",
        "性别",
        "项目",
        "组别",
        "成绩",
        "排名",
        "积分",
        "电话",
    ]
    if list(df.columns) != expected:
        raise HTTPException(status_code=400, detail="表头不匹配")
    db.execute(delete(Athlete))
    db.execute(delete(Grouping))
    db.execute(delete(Result))
    db.execute(delete(PersonalRanking))
    db.execute(delete(CollegeRanking))
    db.commit()
    global LAST_IMPORT_TS
    LAST_IMPORT_TS = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    for _, row in df.iterrows():
        athlete = Athlete(
            college=str(row["学院"]).strip(),
            name=str(row["姓名"]).strip(),
            student_id=str(row["学号"]).strip(),
            gender=str(row["性别"]).strip(),
            event=str(row["项目"]).strip(),
            group_name=str(row["组别"]).strip() if not pd.isna(row["组别"]) else None,
            score=float(row["成绩"]) if not pd.isna(row["成绩"]) else None,
            rank=int(row["排名"]) if not pd.isna(row["排名"]) else None,
            points=int(row["积分"]) if not pd.isna(row["积分"]) else None,
            phone=str(row["电话"]).strip() if not pd.isna(row["电话"]) else None,
        )
        existing = db.scalar(
            select(Athlete).where(
                Athlete.student_id == athlete.student_id,
                Athlete.event == athlete.event,
            )
        )
        if existing:
            for key, value in athlete.__dict__.items():
                if key.startswith("_"):
                    continue
                setattr(existing, key, value)
        else:
            db.add(athlete)
    db.commit()
    # Update event participant counts without clearing historical records.
    athletes = db.scalars(select(Athlete)).all()
    counts = {}
    for athlete in athletes:
        counts[athlete.event] = counts.get(athlete.event, 0) + 1
    existing_events = {e.name: e for e in db.scalars(select(Event)).all()}
    for event_name, event in existing_events.items():
        event.participant_count = counts.get(event_name, 0)
    for event_name, count in counts.items():
        if event_name in existing_events:
            existing_events[event_name].participant_count = count
        else:
            db.add(
                Event(
                    name=event_name,
                    participant_count=count,
                    best_record=None,
                    record_holder="暂无",
                )
            )
    db.commit()
    return {"message": "imported"}


@app.get("/athletes/export")
def export_athletes(db: Session = Depends(get_db)):
    rows = db.scalars(select(Athlete)).all()
    data = [
        {
            "学院": r.college,
            "姓名": r.name,
            "学号": r.student_id,
            "性别": r.gender,
            "项目": r.event,
            "组别": r.group_name or "",
            "成绩": r.score if r.score is not None else "",
            "排名": r.rank if r.rank is not None else "",
            "积分": r.points if r.points is not None else "",
            "电话": r.phone or "",
        }
        for r in rows
    ]
    timestamp = get_timestamp()
    return excel_response(data, f"athletes_{timestamp}.xlsx")


@app.get("/athletes/template")
def export_athletes_template():
    data = [
        {
            "学院": "",
            "姓名": "",
            "学号": "",
            "性别": "",
            "项目": "",
            "组别": "",
            "成绩": "",
            "排名": "",
            "积分": "",
            "电话": "",
        }
    ]
    timestamp = get_timestamp()
    return excel_response(data, f"athletes_template_{timestamp}.xlsx")


@app.get("/groups")
def list_groups(
    event: Optional[str] = None,
    gender: Optional[str] = None,
    round: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(Grouping)
    if event:
        query = query.where(Grouping.event == event)
    if round:
        query = query.where(Grouping.round == round)
    if gender:
        athlete_query = select(Athlete.student_id)
        if event:
            athlete_query = athlete_query.where(Athlete.event == event)
        athlete_query = athlete_query.where(Athlete.gender == gender)
        student_ids = [row[0] for row in db.execute(athlete_query).all()]
        if not student_ids:
            return []
        query = query.where(Grouping.student_id.in_(student_ids))
    return [to_dict(row) for row in db.scalars(query).all()]


@app.get("/events/list")
def list_events(db: Session = Depends(get_db)):
    return [to_dict(row) for row in db.scalars(select(Event)).all()]


@app.get("/events/options")
def list_event_options(db: Session = Depends(get_db)):
    rows = db.execute(select(distinct(Athlete.event))).all()
    return [row[0] for row in rows if row[0]]


@app.get("/athletes/by-event")
def list_athletes_by_event(event: str, db: Session = Depends(get_db)):
    query = select(Athlete).where(Athlete.event == event)
    return [to_dict(row) for row in db.scalars(query).all()]


@app.get("/groups/candidates")
def list_group_candidates(
    event: str,
    gender: str,
    round: str,
    db: Session = Depends(get_db),
):
    if round == "final":
        prelim_groups = db.scalars(
            select(Grouping).where(
                Grouping.event == event,
                Grouping.round == "prelim",
            )
        ).all()
        if not prelim_groups:
            raise HTTPException(
                status_code=404,
                detail="可能没有预赛分组或没有预赛成绩，请检查后重试",
            )
        scored = []
        for row in prelim_groups:
            if row.prelim_score is None:
                continue
            scored.append({"student_id": row.student_id, "score": row.prelim_score})
        ranked_ids = [r["student_id"] for r in rank_athletes_by_score(scored, event)[:8]]
        if not ranked_ids:
            raise HTTPException(
                status_code=404,
                detail="可能没有预赛分组或没有预赛成绩，请检查后重试",
            )
        athletes = db.scalars(
            select(Athlete).where(
                Athlete.event == event,
                Athlete.gender == gender,
                Athlete.student_id.in_(ranked_ids),
            )
        ).all()
        return [to_dict(row) for row in athletes]

    athletes = db.scalars(
        select(Athlete).where(
            Athlete.event == event,
            Athlete.gender == gender,
        )
    ).all()
    return [to_dict(row) for row in athletes]


@app.get("/results/list")
def list_results(
    event: Optional[str] = None,
    name: Optional[str] = None,
    student_id: Optional[str] = None,
    round: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if round and round != "final":
        base_query = select(Grouping).where(Grouping.round == round)
        if event:
            base_query = base_query.where(Grouping.event == event)
        base_rows = db.scalars(base_query).all()

        query = select(Grouping).where(Grouping.round == round)
        if event:
            query = query.where(Grouping.event == event)
        if name:
            query = query.where(Grouping.name == name)
        if student_id:
            query = query.where(Grouping.student_id == student_id)
        rows = db.scalars(query).all()
        scores = []
        for row in base_rows:
            if round == "prelim":
                score = row.prelim_score
                date = row.prelim_date
            elif round == "semi":
                score = row.semi_score
                date = row.semi_date
            else:
                score = row.final_score
                date = row.final_date
            if score is None:
                continue
            scores.append({"student_id": row.student_id, "score": score})
        ranked = {
            r["student_id"]: r["rank"]
            for r in rank_athletes_by_score(scores, event or "")
        }
        payload = []
        for row in rows:
            if round == "prelim":
                score = row.prelim_score
                date = row.prelim_date
            elif round == "semi":
                score = row.semi_score
                date = row.semi_date
            else:
                score = row.final_score
                date = row.final_date
            payload.append(
                {
                    "id": row.id,
                    "event": row.event,
                    "name": row.name,
                    "student_id": row.student_id,
                    "college": row.college,
                    "score": score,
                    "rank": ranked.get(row.student_id),
                    "date": date,
                    "round": round,
                }
            )
        return payload

    query = select(Result)
    if event:
        query = query.where(Result.event == event)
    if name:
        query = query.where(Result.name == name)
    if student_id:
        query = query.where(Result.student_id == student_id)
    return [to_dict(row) for row in db.scalars(query).all()]


@app.get("/rankings/personal/list")
def list_personal_rankings(db: Session = Depends(get_db)):
    return [to_dict(row) for row in db.scalars(select(PersonalRanking)).all()]


@app.get("/rankings/college/list")
def list_college_rankings(db: Session = Depends(get_db)):
    return [to_dict(row) for row in db.scalars(select(CollegeRanking)).all()]


@app.post("/groups/generate")
def generate_groups(req: GroupGenerateRequest, db: Session = Depends(get_db)):
    candidates = db.scalars(
        select(Athlete).where(
            Athlete.event == req.event,
            Athlete.gender == req.gender,
        )
    ).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No athletes found")

    round_value = req.round
    if req.event in MIXED_EVENTS:
        round_value = "one"

    if req.event in MULTI_ROUND_EVENTS and req.round in {"semi", "final"}:
        round_value = req.round
        base_round = "semi" if req.round == "final" else "prelim"
        base_query = select(Grouping).where(
            Grouping.event == req.event,
            Grouping.round == base_round,
        )
        base_rows = db.scalars(base_query).all()
        if base_rows:
            scored = [r for r in base_rows if r.prelim_score is not None or r.semi_score is not None]
            score_field = "semi_score" if req.round == "final" and any(r.semi_score for r in scored) else "prelim_score"
            scored_rows = [
                {
                    "student_id": r.student_id,
                    "score": getattr(r, score_field) or 0,
                }
                for r in scored
            ]
            sorted_ids = [
                r["student_id"]
                for r in rank_athletes_by_score(scored_rows, req.event)[:8 if req.round == "final" else 16]
            ]
            candidates = db.scalars(
                select(Athlete).where(
                    Athlete.student_id.in_(sorted_ids),
                    Athlete.event == req.event,
                )
            ).all()

    ordered = distribute_by_college(candidates)
    groups = []
    group_labels = []
    per_group = req.per_group
    for idx in range(0, len(ordered), per_group):
        label = chr(ord("A") + len(group_labels))
        group_labels.append(label)
        group_members = ordered[idx : idx + per_group]
        random.shuffle(group_members)
        lanes = list(range(1, per_group + 1))
        random.shuffle(lanes)
        for lane_idx, athlete in enumerate(group_members):
            groups.append(
                {
                    "event": athlete.event,
                    "college": athlete.college,
                    "student_id": athlete.student_id,
                    "name": athlete.name,
                    "group_label": label,
                    "lane": lanes[lane_idx] if lane_idx < len(lanes) else None,
                    "round": round_value,
                }
            )
    return {"groups": groups}


@app.post("/groups/confirm")
def confirm_groups(req: GroupConfirmRequest, db: Session = Depends(get_db)):
    db.execute(
        delete(Grouping).where(
            Grouping.event == req.event,
            Grouping.round == req.round,
        )
    )
    for item in req.groups:
        grouping = Grouping(**item.model_dump())
        db.add(grouping)

        athlete = db.scalar(
            select(Athlete).where(
                Athlete.student_id == item.student_id,
                Athlete.event == req.event,
            )
        )
        if athlete:
            athlete.group_name = format_group_name(athlete.gender, item.group_label)
    db.commit()
    return {"message": "saved"}


@app.post("/events/initialize")
def initialize_events(db: Session = Depends(get_db)):
    db.execute(delete(Event))
    db.commit()
    athletes = db.scalars(select(Athlete)).all()
    grouped: Dict[str, List[Athlete]] = {}
    for athlete in athletes:
        grouped.setdefault(athlete.event, []).append(athlete)
    for event_name, items in grouped.items():
        scores = [a.score for a in items if a.score is not None]
        best_record = None
        holder = None
        if scores:
            ordered = sort_scores(scores, event_name)
            best_record = ordered[0]
            holder = next(
                (a.name for a in items if a.score == best_record),
                None,
            )
        event = Event(
            name=event_name,
            participant_count=len(items),
            best_record=best_record,
            record_holder=holder or "暂无",
        )
        db.add(event)
    db.commit()
    return {"message": "initialized"}


@app.post("/results/submit")
def submit_result(req: ResultSubmitRequest, db: Session = Depends(get_db)):
    grouping = db.scalar(
        select(Grouping).where(
            Grouping.student_id == req.student_id,
            Grouping.event == req.event,
            Grouping.round == req.round,
        )
    )
    if not grouping:
        athlete = db.scalar(
            select(Athlete).where(
                Athlete.student_id == req.student_id,
                Athlete.event == req.event,
            )
        )
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")
        grouping = Grouping(
            event=req.event,
            college=athlete.college,
            student_id=athlete.student_id,
            name=athlete.name,
            group_label="A",
            lane=None,
            round=req.round,
        )
        db.add(grouping)
    now = req.date or datetime.utcnow()
    if req.round == "prelim":
        grouping.prelim_score = req.score
        grouping.prelim_date = now
    elif req.round == "semi":
        grouping.semi_score = req.score
        grouping.semi_date = now
    else:
        grouping.final_score = req.score
        grouping.final_date = now

    if req.round in {"final", "one"}:
        update_final_results(req.event, db)
    db.commit()
    if req.round in {"final", "one"} and req.date:
        result_row = db.scalar(
            select(Result).where(
                Result.event == req.event,
                Result.student_id == req.student_id,
            )
        )
        if result_row:
            result_row.date = req.date
            db.commit()
    return {"message": "saved"}


@app.post("/results/initialize")
def initialize_results(db: Session = Depends(get_db)):
    db.execute(delete(Result))
    db.commit()
    events = db.scalars(select(Event)).all()
    for event in events:
        update_final_results(event.name, db)
    db.commit()
    return {"message": "initialized"}


@app.post("/rankings/personal/initialize")
def initialize_personal_rankings(db: Session = Depends(get_db)):
    db.execute(delete(PersonalRanking))
    db.commit()
    results = db.scalars(select(Result)).all()
    total_points_by_student: Dict[str, int] = {}
    for result in results:
        points = points_for_rank(result.rank)
        bonus = 0
        event = db.scalar(select(Event).where(Event.name == result.event))
        if event and event.best_record is not None:
            if (is_distance_event(event.name) and result.score > event.best_record) or (
                not is_distance_event(event.name) and result.score < event.best_record
            ):
                bonus = 9
        total_points_by_student[result.student_id] = (
            total_points_by_student.get(result.student_id, 0) + points + bonus
        )
        ranking = PersonalRanking(
            student_id=result.student_id,
            name=result.name,
            college=result.college,
            event=result.event,
            score=result.score,
            rank=result.rank,
            points=points + bonus,
            total_points=0,
        )
        db.add(ranking)
    db.commit()

    rankings = db.scalars(select(PersonalRanking)).all()
    for ranking in rankings:
        ranking.total_points = total_points_by_student.get(ranking.student_id, 0)
        athlete = db.scalar(
            select(Athlete).where(
                Athlete.student_id == ranking.student_id,
                Athlete.event == ranking.event,
            )
        )
        if athlete:
            athlete.points = ranking.points
    db.commit()
    return {"message": "initialized"}


@app.post("/rankings/college/initialize")
def initialize_college_rankings(db: Session = Depends(get_db)):
    db.execute(delete(CollegeRanking))
    db.commit()
    rankings = db.scalars(select(PersonalRanking)).all()
    grouped: Dict[str, Dict[str, int]] = {}
    for ranking in rankings:
        item = grouped.setdefault(ranking.college, {"points": 0, "events": set(), "participants": set()})
        item["points"] += ranking.points
        item["events"].add(ranking.event)
        item["participants"].add(ranking.student_id)

    for college, info in grouped.items():
        db.add(
            CollegeRanking(
                college=college,
                event_count=len(info["events"]),
                participant_count=len(info["participants"]),
                total_points=info["points"],
            )
        )
    db.commit()
    return {"message": "initialized"}


@app.get("/export/groups")
def export_groups(db: Session = Depends(get_db)):
    rows = db.scalars(select(Grouping)).all()
    data = [
        {
            "项目": r.event,
            "学院": r.college,
            "学号": r.student_id,
            "姓名": r.name,
            "组别": r.group_label,
            "道次": r.lane or "",
            "预赛成绩": r.prelim_score or "",
            "决赛成绩": r.final_score or "",
        }
        for r in rows
    ]
    timestamp = get_timestamp()
    return excel_response(data, f"groups_{timestamp}.xlsx")


@app.get("/export/events")
def export_events(db: Session = Depends(get_db)):
    rows = db.scalars(select(Event)).all()
    data = [
        {
            "项目": r.name,
            "人数": r.participant_count,
            "历史最高纪录": r.best_record if r.best_record is not None else "暂无",
            "最高记录保持者": r.record_holder or "暂无",
        }
        for r in rows
    ]
    timestamp = get_timestamp()
    return excel_response(data, f"events_{timestamp}.xlsx")


@app.get("/export/results")
def export_results(
    event: Optional[str] = None,
    name: Optional[str] = None,
    student_id: Optional[str] = None,
    round: Optional[str] = None,
    db: Session = Depends(get_db),
):
    data = []
    if round and round != "final":
        query = select(Grouping)
        if event:
            query = query.where(Grouping.event == event)
        if name:
            query = query.where(Grouping.name == name)
        if student_id:
            query = query.where(Grouping.student_id == student_id)
        if round:
            query = query.where(Grouping.round == round)
        rows = db.scalars(query).all()
        scores = []
        for row in rows:
            if round == "prelim":
                score = row.prelim_score
            elif round == "semi":
                score = row.semi_score
            else:
                score = row.final_score
            if score is None:
                continue
            scores.append({"student_id": row.student_id, "score": score})
        ranked = {
            r["student_id"]: r["rank"]
            for r in rank_athletes_by_score(scores, event or "")
        }
        for r in rows:
            if round == "prelim":
                score = r.prelim_score
                date = r.prelim_date
            elif round == "semi":
                score = r.semi_score
                date = r.semi_date
            else:
                score = r.final_score
                date = r.final_date
            data.append(
                {
                    "项目": r.event,
                    "姓名": r.name,
                    "学号": r.student_id,
                    "学院": r.college,
                    "成绩": score if score is not None else "",
                    "排名": ranked.get(r.student_id, ""),
                    "日期": date.strftime("%Y-%m-%d %H:%M:%S") if date else "",
                }
            )
    else:
        query = select(Result)
        if event:
            query = query.where(Result.event == event)
        if name:
            query = query.where(Result.name == name)
        if student_id:
            query = query.where(Result.student_id == student_id)
        rows = db.scalars(query).all()
        data = [
            {
                "项目": r.event,
                "姓名": r.name,
                "学号": r.student_id,
                "学院": r.college,
                "成绩": r.score,
                "排名": r.rank,
                "日期": r.date.strftime("%Y-%m-%d") if r.date else "",
            }
            for r in rows
        ]
    timestamp = get_timestamp()
    return excel_response(data, f"results_{timestamp}.xlsx")


@app.get("/export/personal-rankings")
def export_personal_rankings(db: Session = Depends(get_db)):
    rows = db.scalars(select(PersonalRanking)).all()
    data = [
        {
            "学号": r.student_id,
            "姓名": r.name,
            "学院": r.college,
            "项目": r.event,
            "成绩": r.score,
            "排名": r.rank,
            "积分": r.points,
            "总积分": r.total_points,
        }
        for r in rows
    ]
    timestamp = get_timestamp()
    return excel_response(data, f"personal_rankings_{timestamp}.xlsx")


@app.get("/export/college-rankings")
def export_college_rankings(db: Session = Depends(get_db)):
    rows = db.scalars(select(CollegeRanking)).all()
    data = [
        {
            "学院": r.college,
            "项目数量": r.event_count,
            "参加人数": r.participant_count,
            "学院总计分": r.total_points,
        }
        for r in rows
    ]
    timestamp = get_timestamp()
    return excel_response(data, f"college_rankings_{timestamp}.xlsx")


def format_group_name(gender: str, group_label: str) -> str:
    if gender in {"男", "男子", "male"}:
        prefix = "男子"
    elif gender in {"女", "女子", "female"}:
        prefix = "女子"
    else:
        prefix = "混合"
    return f"{prefix}{group_label}组"


def excel_response(data: List[Dict], filename: str):
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers
    )


def update_final_results(event_name: str, db: Session):
    group_rows = db.scalars(
        select(Grouping).where(
            Grouping.event == event_name,
        )
    ).all()
    final_scores = []
    for row in group_rows:
        score = row.final_score if row.final_score is not None else (
            row.prelim_score if row.round == "one" else None
        )
        if score is not None:
            final_scores.append(
                {
                    "student_id": row.student_id,
                    "score": score,
                }
            )
    ranked = rank_athletes_by_score(final_scores, event_name)
    db.execute(delete(Result).where(Result.event == event_name))
    best_candidate = ranked[0] if ranked else None
    event_row = db.scalar(select(Event).where(Event.name == event_name))
    if best_candidate:
        if not event_row:
            event_row = Event(
                name=event_name,
                participant_count=0,
                best_record=None,
                record_holder=None,
            )
            db.add(event_row)
        should_update = False
        if event_row.best_record is None:
            should_update = True
        else:
            if is_distance_event(event_name):
                should_update = best_candidate["score"] > event_row.best_record
            else:
                should_update = best_candidate["score"] < event_row.best_record
        if should_update:
            athlete = db.scalar(
                select(Athlete).where(
                    Athlete.student_id == best_candidate["student_id"],
                    Athlete.event == event_name,
                )
            )
            event_row.best_record = best_candidate["score"]
            event_row.record_holder = athlete.name if athlete else "鏆傛棤"
    for row in ranked:
        athlete = db.scalar(
            select(Athlete).where(
                Athlete.student_id == row["student_id"],
                Athlete.event == event_name,
            )
        )
        if not athlete:
            continue
        result = Result(
            event=event_name,
            name=athlete.name,
            student_id=athlete.student_id,
            college=athlete.college,
            score=row["score"],
            rank=row["rank"],
            date=datetime.utcnow(),
            round="final",
        )
        db.add(result)
        athlete.score = row["score"]
        athlete.rank = row["rank"]
