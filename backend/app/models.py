from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    UniqueConstraint,
)
from .db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    school = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    must_reset = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Athlete(Base):
    __tablename__ = "athletes"
    id = Column(Integer, primary_key=True, index=True)
    college = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    student_id = Column(String(50), nullable=False, index=True)
    gender = Column(String(10), nullable=False)
    event = Column(String(100), nullable=False)
    group_name = Column(String(50), nullable=True)
    score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)
    points = Column(Integer, nullable=True)
    phone = Column(String(50), nullable=True)
    record_broken = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("student_id", "event", name="uq_athlete_event"),
    )


class Grouping(Base):
    __tablename__ = "groupings"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(100), nullable=False)
    college = Column(String(100), nullable=False)
    student_id = Column(String(50), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    group_label = Column(String(10), nullable=False)
    lane = Column(Integer, nullable=True)
    prelim_score = Column(Float, nullable=True)
    semi_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    prelim_date = Column(DateTime, nullable=True)
    semi_date = Column(DateTime, nullable=True)
    final_date = Column(DateTime, nullable=True)
    round = Column(String(20), nullable=False, default="prelim")

    __table_args__ = (
        UniqueConstraint(
            "student_id", "event", "round", name="uq_grouping_event_round"
        ),
    )


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    participant_count = Column(Integer, nullable=False, default=0)
    best_record = Column(Float, nullable=True)
    record_holder = Column(String(100), nullable=True)


class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    student_id = Column(String(50), nullable=False)
    college = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    round = Column(String(20), nullable=False, default="final")

    __table_args__ = (
        UniqueConstraint("student_id", "event", "round", name="uq_result_event_round"),
    )




class ResultDistance(Base):
    __tablename__ = "results_distance"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    student_id = Column(String(50), nullable=False)
    college = Column(String(100), nullable=False)
    prelim_attempt1 = Column(Float, nullable=True)
    prelim_attempt2 = Column(Float, nullable=True)
    prelim_attempt3 = Column(Float, nullable=True)
    prelim_best = Column(Float, nullable=True)
    final_attempt1 = Column(Float, nullable=True)
    final_attempt2 = Column(Float, nullable=True)
    final_attempt3 = Column(Float, nullable=True)
    final_best = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("student_id", "event", name="uq_result_distance_event"),
    )




class ResultJump(Base):
    __tablename__ = "results_jump"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    student_id = Column(String(50), nullable=False)
    college = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    round = Column(String(20), nullable=False, default="final")

    __table_args__ = (
        UniqueConstraint("student_id", "event", "round", name="uq_result_jump_event_round"),
    )



class ResultJumpTemplate(Base):
    __tablename__ = "results_jump_template"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String(100), nullable=False, default="跳高")
    round = Column(String(20), nullable=False, default="final")
    serial_no = Column(Integer, nullable=True)
    name = Column(String(50), nullable=False)
    student_id = Column(String(50), nullable=False, index=True)
    college = Column(String(100), nullable=False)

    # 10组高度，每组3次试跳（对应 D2:AG2 每3格合并）
    h1_try1 = Column(String(10), nullable=True)
    h1_try2 = Column(String(10), nullable=True)
    h1_try3 = Column(String(10), nullable=True)
    h2_try1 = Column(String(10), nullable=True)
    h2_try2 = Column(String(10), nullable=True)
    h2_try3 = Column(String(10), nullable=True)
    h3_try1 = Column(String(10), nullable=True)
    h3_try2 = Column(String(10), nullable=True)
    h3_try3 = Column(String(10), nullable=True)
    h4_try1 = Column(String(10), nullable=True)
    h4_try2 = Column(String(10), nullable=True)
    h4_try3 = Column(String(10), nullable=True)
    h5_try1 = Column(String(10), nullable=True)
    h5_try2 = Column(String(10), nullable=True)
    h5_try3 = Column(String(10), nullable=True)
    h6_try1 = Column(String(10), nullable=True)
    h6_try2 = Column(String(10), nullable=True)
    h6_try3 = Column(String(10), nullable=True)
    h7_try1 = Column(String(10), nullable=True)
    h7_try2 = Column(String(10), nullable=True)
    h7_try3 = Column(String(10), nullable=True)
    h8_try1 = Column(String(10), nullable=True)
    h8_try2 = Column(String(10), nullable=True)
    h8_try3 = Column(String(10), nullable=True)
    h9_try1 = Column(String(10), nullable=True)
    h9_try2 = Column(String(10), nullable=True)
    h9_try3 = Column(String(10), nullable=True)
    h10_try1 = Column(String(10), nullable=True)
    h10_try2 = Column(String(10), nullable=True)
    h10_try3 = Column(String(10), nullable=True)

    score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)
    remark = Column(String(255), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "event", "round", name="uq_result_jump_template_event_round"),
    )


class PersonalRanking(Base):
    __tablename__ = "personal_rankings"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    college = Column(String(100), nullable=False)
    event = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    total_points = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "event", name="uq_personal_event"),
    )


class CollegeRanking(Base):
    __tablename__ = "college_rankings"
    id = Column(Integer, primary_key=True, index=True)
    college = Column(String(100), unique=True, nullable=False)
    event_count = Column(Integer, nullable=False)
    participant_count = Column(Integer, nullable=False)
    total_points = Column(Integer, nullable=False)


class TeamRankingManualBonus(Base):
    __tablename__ = "team_ranking_manual_bonus"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), nullable=False)
    event = Column(String(100), nullable=False)
    manual_points = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "event", name="uq_team_ranking_manual_bonus"),
    )

