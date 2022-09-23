from multiprocessing.sharedctypes import Value
import os
import requests
from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import Unauthorized
from models import db, connect_db, User, Goals, Comments
from forms import LoginForm, RegisterForm, CommentForm, GoalsForm, EditGoalsForm
from passes import Authorization, SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///exercise2'))
# prodURI = os.getenv('DATABASE_URL')
# prodURI = prodURI.replace("postgres://", "postgresql://")
# app.config['SQLALCHEMY_DATABASE_URI'] = prodURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', SECRET_KEY)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

API_BASE_URL = "https://wger.de/api/v2"

connect_db(app)
db.create_all()

db = SQLAlchemy(app)

debug = DebugToolbarExtension(app)


muscle_groups = { "chest":
                    {
                        "muscle": "Chest",
                        'image': "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-pectoralis-major-pectoralis-major-157612533.jpg",
                        'id': '4',
                        "muscle_image": "/static/images/muscles/main/muscle-4.svg",
                        "body_image": "/static/images/muscles/muscular_system_front.svg"
                    },
                "biceps":
                    {
                        "muscle": "Biceps",
                        "image": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-biceps-biceps-157612447.jpg", "id": "1",
                        "muscle_image": "/static/images/muscles/main/muscle-1.svg", 
                        "body_image": "/static/images/muscles/muscular_system_front.svg"},
                "abs":
                    {
                        "muscle": "Abs",
                        "image": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-external-oblique-external-oblique-157612399.jpg",
                        "id": "14",
                        "muscle_image": "/static/images/muscles/main/muscle-14.svg",
                        "body_image": "/static/images/muscles/muscular_system_front.svg"},
                "shoulders":
                    {
                        "muscle": "Shoulders",
                        "image": "https://thumbs.dreamstime.com/b/deltoid-d-rendered-muscle-illustration-157612398.jpg",
                        "id": "2",
                        "muscle_image": "/static/images/muscles/main/muscle-2.svg",
                        "body_image": "/static/images/muscles/muscular_system_front.svg"},
                "quads":
                    {
                        "muscle": "Quads",
                        "image": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-vastus-lateralis-vastus-lateralis-157612633.jpg",
                        "id": "10",
                        "muscle_image": "/static/images/muscles/main/muscle-10.svg",
                        "body_image": "/static/images/muscles/muscular_system_front.svg"},
                "traps":
                    {
                        "muscle": "Traps",
                        "image": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-trapezius-trapezius-157612310.jpg",
                        "id": "9",
                        "muscle_image": "/static/images/muscles/main/muscle-9.svg",
                        "body_image": "/static/images/muscles/muscular_system_back.svg"},
                "back":
                    {
                        "muscle": "Back",
                        "image": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-latissimus-dorsi-latissimus-dorsi-157612158.jpg",
                        "id": "12",
                        "muscle_image": "/static/images/muscles/main/muscle-12.svg",
                        "body_image": "/static/images/muscles/muscular_system_back.svg"},
                "triceps":
                    {
                        "muscle": "Triceps",
                        "image": "https://thumbs.dreamstime.com/b/triceps-d-rendered-muscle-illustration-157612423.jpg",
                        "id": "5",
                        "muscle_image": "/static/images/muscles/main/muscle-5.svg",
                        "body_image": "/static/images/muscles/muscular_system_back.svg"},
                "calves": 
                    {
                        "muscle": "Calves",
                        "image": "https://thumbs.dreamstime.com/b/gastrocnemius-d-rendered-muscle-illustration-157612044.jpg", "id": "7",
                        "muscle_image": "/static/images/muscles/main/muscle-7.svg",
                        "body_image": "/static/images/muscles/muscular_system_back.svg"},
                "hamstrings":
                    {
                        "muscle": "Hamstrings",
                        "image": "https://thumbs.dreamstime.com/b/biceps-femoris-longus-d-rendered-muscle-illustration-157611954.jpg",
                        "id": "11",
                        "muscle_image": "/static/images/muscles/main/muscle-11.svg",
                        "body_image": "/static/images/muscles/muscular_system_back.svg"},
                "glutes": 
                    {
                        "muscle": "Glutes",
                        "image": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-gluteus-maximus-gluteus-maximus-157612061.jpg",
                        "id": "8",
                        "muscle_image": "/static/images/muscles/main/muscle-8.svg",
                        "body_image": "/static/images/muscles/muscular_system_back.svg"}}


@app.route('/')
def homepage():
    '''showcase the route to the homepage, where you have the option of logging in/registering or just choosing your muscle group to find workouts in'''
    return render_template('home.html')



#**************************************************************************** USERS ******************************************************************************

@app.route('/register', methods = ["GET", "POST"])
def register_user():
    """Have new users make an account"""

    if "username" in session:
        return redirect(f"/user/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        birthday = form.birthday.data

        new_user = User.register(username, password, first_name, last_name, birthday)
        # print(username)
        # print(password)
        # print(first_name)
        # print(last_name)
        # print(birthday)
        # print(new_user)
        # print(form.errors)

        db.session.add(new_user)
        # current_db_sessions = db.session.object_session(new_user)
        # current_db_sessions.add(new_user)
        db.session.commit()
        session["username"] = new_user.username
        return redirect(f"/user/{new_user.username}")

    else:
        return render_template("users/register.html", form = form)



@app.route('/login', methods = ["GET", "POST"])
def login_user():
    """Have an existing user loging to their account"""

    if "username" in session:
        return redirect(f"/user/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f"/user/{user.username}")
        else:
            form.username.errors['Invalid username/password']
            return render_template("users/login.html", form = form)

    return render_template("users/login.html", form = form)


@app.route("/logout")
def logout_user():
    """Logout the user"""
    session.pop('username')
    return redirect('/login')


@app.route('/user/<username>')
def show_user(username):
    """Page of the users profile"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)
    goal = Goals.query.get(username)

    return render_template("users/show.html", user = user, goal = goal)


@app.route("/user/<username>/delete", methods = ["GET", "POST"])
def remove_user(username):
    """Removing the user from the DB"""
    
    if "username" not in session or username != session["username"]:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect('/login')


#**************************************************************************** GOALS ******************************************************************************

@app.route('/user/<username>/goals', methods = ["GET", "POST"])
def set_goals(username):
    """Show the goals form"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = GoalsForm()
    user = User.query.get(username)

    if form.validate_on_submit():
        current_weight = form.current_weight.data
        goal_weight = form.goal_weight.data

        goals = Goals(current_weight = current_weight, goal_weight = goal_weight, user = user)

        db.session.add(goals)
        db.session.commit()

        return redirect(f"/user/{username}")

    else:
        return render_template("goals/new-goals.html", form = form)



@app.route("/user/<username>/goals/update", methods = ["GET", "POST"])
def update_goals(username):
    """Show the update-goals form and run it when submitted"""

    goals = Goals.query.get(username)

    if "username" not in session or goals.username != session['username']:
        return Unauthorized()

    form = EditGoalsForm(obj = goals)

    if form.validate_on_submit():
        goals.current_weight = form.current_weight.data
        goals.goal_weight = form.goal_weight.data

        db.session.commit()

        return redirect(f"/user/{goals.username}")

    return render_template("goals/edit.html", form = form, goals = goals)




#************************************************************************* MUSCLE GROUPS ***************************************************************************

@app.route('/workouts')
def show_workouts():
    return render_template('muscles.html', muscle_groups = muscle_groups)

def make_api_request(muscle_id):
    url = f"{API_BASE_URL}/exercise/?muscles={muscle_id}&language=2"
    data = '{"key": "results"}'
    headers = {'Accept': 'application/json', 'Authorization': Authorization}
    response = requests.get(url = url, data = data, headers = headers)
    return response.json()

# def add_comment():
#     form = CommentForm()

#     form.validate_on_submit()
#     name = form.name.data
#     title = form.title.data
#     content = form.content.data
#     date_posted = form.date_posted.data
#     workout_id = form.workout_id.data

#     comment = Comments(name = name, title = title, content = content, date_posted = date_posted, workout_id = workout_id)

#     db.session.add(comment)
#     db.session.commit()

    
#     return redirect(request.url)


@app.route('/muscle/<muscle_name>', methods = ["GET", "POST"])
def specific_workouts(muscle_name):
    """Show the workouts that are offered for the muscle selected"""

    form = CommentForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            title = form.title.data
            content = form.content.data
            date_posted = form.date_posted.data
            workout_id = form.workout_id.data

            comment = Comments(name = name, title = title, content = content, date_posted = date_posted, workout_id = workout_id)

            db.session.add(comment)
            db.session.commit()

            return redirect(request.url)
    else: 
        muscle_group = muscle_groups[muscle_name]
        muscle_id = muscle_groups[muscle_name].get('id')
        workout = make_api_request(muscle_id)
        workouts = workout['results']
        comment = Comments.query.all()
        

        return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment, muscle_group = muscle_group)


# @app.route('/muscle/<muscle_name>', methods = ["POST"])
# def add_chest_comment(muscle_name):
#     """Show the comment form"""

#     muscle_group = muscle_groups[muscle_name]
#     add_comment()
#     return redirect(request.url)

