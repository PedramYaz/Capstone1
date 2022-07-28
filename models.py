'''models for the exercise app'''

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

bcrypt = Bcrypt()


class User(db.Model):
    """Creating a User model"""

    __tablename__ = "users"

    # id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, primary_key = True, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String, nullable = False)
    birthday = db.Column(db.Date, nullable = False)

    goals = db.relationship("Goals", backref = "user", cascade = "all,delete")
    # comments = db.relationship("Comments", backref = "user", cascade = "all,delete")


    @classmethod
    def register(cls, username, password, first_name, last_name, birthday):
        '''register the user with a hashed password and return the user'''

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username = username,
            password = hashed_utf8,
            first_name = first_name,
            last_name = last_name,
            birthday = birthday
        )
        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, username, password):
        '''validate that the user exists & that the password is correct. 
        return the user if valid; else return false'''

        u = User.query.filter_by(username = username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

class Goals(db.Model):
    """Table for the users goals"""

    __tablename__ = "goals"

    # id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String, db.ForeignKey("users.username"), primary_key = True, nullable = False)
    current_weight = db.Column(db.Float, nullable = False)
    goal_weight = db.Column(db.Float, nullable = True)

    users = db.relationship("User")

    def __repr__(self):
        return f"<Goals username={self.username} current_weight={self.current_weight} goal_weight={self.goal_weight}>"


class Comments(db.Model):
    """Table to store comments that the users leave on the workouts"""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String, nullable = False)
    title = db.Column(db.String, nullable = False)
    content = db.Column(db.Text, nullable = False)
    date_posted = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    workout_id = db.Column(db.Text, nullable = False)