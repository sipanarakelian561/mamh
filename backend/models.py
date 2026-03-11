from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key = True)
    
    #auth / identity fields
    email = db.Column(db.String(255), unique = True, nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)
    
    #role fields
    role = db.Column(db.String(20), nullable=False, index=True)
    
    #profile
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    classrooms = db.relationship("Classroom", back_populates="teacher", cascade="all, delete-orphan")
    enrollments = db.relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    
    __table_args__ = (
        db.CheckConstraint("role IN ('teacher','student')", name="ck_user_role"),
    )


class StudentProgress(db.Model):
    #links students to their teachers and tracks progress
    __tablename__ = "student_progress"
    
    id = db.Column(db.Integer, primary_key = True)
    
    enrollment_id = db.Column(
        db.Integer,
        db.ForeignKey("enrollments.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    
    total_questions_answered = db.Column(db.Integer, default=0, nullable=False)
    correct_answers = db.Column(db.Integer, default=0, nullable=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    enrollment = db.relationship("Enrollment", back_populates="progress")


class Classroom(db.Model):
    __tablename__ = "classrooms"
    
    id = db.Column(db.Integer, primary_key = True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    join_code = db.Column(db.String(12), unique = True, nullable = False, index = True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    teacher = db.relationship("User", back_populates="classrooms")
    enrollments = db.relationship("Enrollment", back_populates="classroom", cascade="all, delete-orphan")

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key = True)
    classroom_id = db.Column(db.Integer, db.ForeignKey("classrooms.id"), nullable=False, index = True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    classroom = db.relationship("Classroom", back_populates="enrollments")
    student = db.relationship("User", back_populates="enrollments")
    progress = db.relationship("StudentProgress", back_populates="enrollment", cascade="all, delete-orphan", uselist=False)
    
    __table_args__ = (
            db.UniqueConstraint("classroom_id", "student_id", name="uq_classroom_student"),
    )