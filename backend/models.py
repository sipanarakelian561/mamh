from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key = True)
    
    #auth / identity fields
    email = db.Column(db.String(255), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    
    #role fields
    role = db.Column(db.String(30), nullable=False, index=True)
    
    #profile
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    students = db.relationship(
        "StudentProgress",
        foreign_keys="StudentProgress.teacher_id",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )
    
    progress = db.relationship(
        "StudentProgress",
        foreign_keys="StudentProgress.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    
class StudentProgress(db.Model):
    __tablename__ = "student_progress"
    
    id = db.Column(db.Integer, primary_key = True)
    
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    total_questions_answered = db.Column(db.Integer, default=0, nullable=False)
    correct_answers = db.Column(db.Integer, default=0, nullable=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    teacher = db.relationship("User", foreign_keys=[teacher_id], back_populates="students")
    student = db.relationship("User", foreign_keys=[student_id], back_populates="progress")
    
    __table_args__ = (
            db.UniqueConstraint("teacher_id", "student_id", name="uq_teacher_student")
    )
    