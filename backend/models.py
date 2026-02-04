from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# USER TABLE - WHETHER A USER IS A TEACHER OR STUDENT


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # role fields
    role = db.Column(db.String(20), nullable=False, index=True)

    # profile
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    # auth / identity fields
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # When was the account created
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    # If a user is a teacher they have a relationship with the classroom table. If a teacher is deleted so are their classrooms.
    classrooms = db.relationship(
        "Classroom", back_populates="teacher", cascade="all, delete-orphan")

    # If a user is a student they have a relationshiip with the enrollment table. If a student is deleted they are no longer in the enrollemnt table.
    enrollments = db.relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan")

    # if a user is a teacher they have a relationship with the problem set table. If a teacher is deleted so are their problem sets.
    problem_sets = db.relationship(
        "ProblemSet", back_populates="teacher", cascade="all, delete-orphan")

    # If a user is a student they have a relationship with the closet_item table (virtual things they own. If a student is deleted so are their closet items.
    closet_items = db.relationship(
        "ClosetItem", back_populates="student", cascade="all, delete-orphan")

    # This constraint says a user must check in as a teacher or student.
    __table_args__ = (
        db.CheckConstraint("role IN ('teacher','student')",
                           name="ck_user_role"),
    )


# STUDENTPROGESS TABLE - A TEACHER AND STUDENT WILL BE ABLE TO LOOK A INDIVIDUALS PROGRESS
class StudentProgress(db.Model):

    __tablename__ = "student_progress"

    id = db.Column(db.Integer, primary_key=True)

    # The number id of a student erolled in a classroom
    enrollment_id = db.Column(db.Integer, db.ForeignKey(
        "enrollments.id"), nullable=False, unique=True, index=True)

    # The number of total questions answered by a student
    total_questions_answered = db.Column(db.Integer, default=0, nullable=False)

    # The number of total questions answered by a student
    correct_answers = db.Column(db.Integer, default=0, nullable=False)

    # Everything a student makes any sort of progress the time is updated.
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    enrollment = db.relationship("Enrollment", back_populates="progress")

# A classroom (class code) created by a teacher


class Classroom(db.Model):
    __tablename__ = "classrooms"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    join_code = db.Column(db.String(12), unique=True,
                          nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    teacher = db.relationship("User", back_populates="classrooms")
    enrollments = db.relationship(
        "Enrollment", back_populates="classroom", cascade="all, delete-orphan")

# Enrollment info. What info of student enrolled in a classroom


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey(
        "classrooms.id"), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), nullable=False, index=True)

    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    classroom = db.relationship("Classroom", back_populates="enrollments")
    student = db.relationship("User", back_populates="enrollments")
    progress = db.relationship(
        "StudentProgress", back_populates="enrollment", cascade="all, delete-orphan", uselist=False)

    __table_args__ = (
        db.UniqueConstraint("classroom_id", "student_id",
                            name="uq_classroom_student"),
    )


# Problem Set overall info (view from outside). Topic name, num of questions, etc
class ProblemSet(db.Model):
    __tablename__ = "problem_sets"

    id = db.Column(db.Integer, primary_key=True)

    # who made this problem set? (teacher user)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), nullable=False, index=True)

    # just a name/topic
    topic_name = db.Column(db.String(255), nullable=False)

    # how many questions are in the set
    num_questions = db.Column(db.Integer, nullable=False)

    # time limit in seconds (or minutes — pick one and stay consistent)
    time_limit = db.Column(db.Integer, nullable=False)

    max_currency = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    teacher = db.relationship("User", back_populates="problem_sets")

    questions = db.relationship(
        "Question", back_populates="problem_set", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("teacher_id", "topic_name", name="uq_teacher_set"),
    )

# Questions -> The questions within a problem set


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)

    # What problem set do these questions belong to
    problem_set_id = db.Column(db.Integer, db.ForeignKey(
        "problem_sets.id"), nullable=False, index=True)
    # The questions themselves
    prompt = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to the problem set
    problem_set = db.relationship("ProblemSet", back_populates="questions")

    answers = db.relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)

    question_id = db.Column(db.Integer, db.ForeignKey(
        "questions.id"), nullable=False, index=True)

    # The text of the answer
    text = db.Column(db.Text, nullable=False)

    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    question = db.relationship("Question", back_populates="answers")

# shop where students can buy customizable things for their monsters / monsters room


class ShopItem(db.Model):
    __tablename__ = "shop_items"

    id = db.Column(db.Integer, primary_key=True)
    # item name - the name of the item
    name = db.Column(db.String(225), nullable=False)
    # item type - shirt, pants, shoes, accessories, mat, bookshelf, poster, bed
    category = db.Column(db.String(50), nullable=False, index=True)
    # price - the price of the item
    price = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    closet_items = db.relationship("ClosetItem", back_populates="shop_item")

    # Restriction - Student cannot but the same item twice


# The closet of the student of items they got from the shop (Inventory of student). Every student has one closet that they can only they can see
class ClosetItem(db.Model):
    __tablename__ = "closet_items"
    # number of item
    id = db.Column(db.Integer, primary_key=True)

    # To which student does this closet belong to
    student_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), nullable=False, index=True)

    # Link to the item in the shop(this is how you get name/category)
    shop_item_id = db.Column(db.Integer, db.ForeignKey(
        "shop_items.id"), nullable=False, index=True)

    # Is the item equipped true or false
    is_equipped = db.Column(db.Boolean, default=False, nullable=False)

    # Price paid for the item
    price_paid = db.Column(db.Integer, nullable=False)

    # When did the student buy it
    purchased_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    shop_item = db.relationship("ShopItem", back_populates="closet_items")
    student = db.relationship("User", back_populates="closet_items")

    __table_args__ = (
        db.UniqueConstraint("student_id", "shop_item_id",
                            name="uq_student_shop_item"),
    )
