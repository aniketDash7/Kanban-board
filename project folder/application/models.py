from .database import db
from flask_login import UserMixin

class Task(db.Model):
    #tasks with status 
    __tablename__ = 'Task'
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    deadline = db.Column(db.String(11))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    #string representation of the title object of task class 
    def __repr__(self):
        return "<Title: {}>".format(self.title)

class User(UserMixin, db.Model):

    #usermixin includes a few methods in the model class that are needed
    #said methods can be created but usermixin does it for you 

    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200),nullable=False)
    password = db.Column(db.String(200),nullable=False)
    task_id = db.relationship('Task', backref='user', lazy='dynamic')
    #string representation of the username object of user class
    def __repr__(self):
        return "<Username: {}>".format(self.username)