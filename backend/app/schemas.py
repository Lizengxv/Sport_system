from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    school: str
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    school: str
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str = Field(min_length=6)


class AthleteBase(BaseModel):
    college: str
    name: str
    student_id: str
    gender: str
    event: str
    group_name: Optional[str] = None
    score: Optional[float] = None
    rank: Optional[int] = None
    points: Optional[int] = None
    phone: Optional[str] = None


class AthleteCreate(AthleteBase):
    pass


class AthleteUpdate(BaseModel):
    college: Optional[str] = None
    name: Optional[str] = None
    student_id: Optional[str] = None
    gender: Optional[str] = None
    event: Optional[str] = None
    group_name: Optional[str] = None
    score: Optional[float] = None
    rank: Optional[int] = None
    points: Optional[int] = None
    phone: Optional[str] = None


class GroupGenerateRequest(BaseModel):
    event: str
    gender: str
    round: str
    per_group: int = 8


class GroupItem(BaseModel):
    event: str
    college: str
    student_id: str
    name: str
    group_label: str
    lane: Optional[int] = None
    round: str


class GroupConfirmRequest(BaseModel):
    event: str
    round: str
    groups: List[GroupItem]


class ResultSubmitRequest(BaseModel):
    event: str
    student_id: str
    round: str
    score: float
    attempt: Optional[int] = None
    date: Optional[datetime] = None


class ResultDistanceSubmitRequest(BaseModel):
    event: str
    student_id: str
    round: str
    attempt: int
    score: float
    date: Optional[datetime] = None
