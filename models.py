from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column('id', db.Integer, primary_key=True)
    text = db.Column('text', db.Text)


class Applicant(db.Model):
    __tablename__ = "applicants"

    id = db.Column('id', db.Integer, primary_key=True)
    age = db.Column('age', db.Integer)
    gender = db.Column('gender', db.Text)
    education = db.Column('education', db.Text)
    source = db.Column('source', db.Text)
    answers = db.relationship("Answer")


class Answer(db.Model):
    __tablename__ = "answers"

    applicant_id = db.Column(
                            'applicant_id',
                            db.Integer,
                            db.ForeignKey('applicants.id'),
                            primary_key=True
                            )
    question_id = db.Column(
                            'question_id',
                            db.Integer,
                            db.ForeignKey('questions.id'),
                            primary_key=True
                            )
    answer = db.Column('answer', db.Integer, primary_key=True)
    question = db.relationship("Question")
