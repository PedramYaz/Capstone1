'''forms for the exercise app'''

from email.policy import default
from wsgiref.validate import validator
from wtforms import SelectField, StringField, TextAreaField, DateField, PasswordField, FloatField, DateTimeField, HiddenField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):
    """Form to register as a user"""
    username = StringField("Username", validators = [InputRequired()])
    password = PasswordField("Password", validators = [InputRequired()])
    first_name = StringField("First Name", validators = [InputRequired()])
    last_name = StringField("Last Name", validators = [InputRequired()])
    birthday = DateField("Birthday", validators = [InputRequired()])

class LoginForm(FlaskForm):
    """Form to login to your account"""
    username = StringField("Username", validators = [InputRequired()])
    password = PasswordField("Password", validators = [InputRequired()])

class CommentForm(FlaskForm):
    """Form to write a comment"""
    name = StringField("Name (optional)")
    title = StringField("Title", validators = [InputRequired()])
    content = TextAreaField("Content", validators = [InputRequired()])
    date_posted = DateField("Date")
    workout_id = HiddenField("Workout ID", validators = [InputRequired()])

class GoalsForm(FlaskForm):
    """Form to fill out your goals"""
    current_weight = FloatField("Current weight")
    goal_weight = FloatField("Goal weight")

class EditGoalsForm(FlaskForm):
    """Form to fill out your goals"""
    current_weight = FloatField("Current weight")
    goal_weight = FloatField("Goal weight")


class DeleteCommentForm(FlaskForm):
    '''fill out'''

class DeleteUserForm(FlaskForm):
    '''fill out'''