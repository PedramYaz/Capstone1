from multiprocessing.sharedctypes import Value
import os
import requests
from flask import Flask, redirect, render_template, flash, jsonify, session, request, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import Unauthorized
from models import db, connect_db, User, Goals, Comments
from forms import LoginForm, RegisterForm, CommentForm, DeleteCommentForm, GoalsForm, EditGoalsForm
from passes import Authorization, SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///exercise'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', SECRET_KEY)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

API_BASE_URL = "https://wger.de/api/v2"

connect_db(app)
db.create_all()

db = SQLAlchemy(app)

debug = DebugToolbarExtension(app)


muscle_groups = [{"chest": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-pectoralis-major-pectoralis-major-157612533.jpg",
                "biceps": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-biceps-biceps-157612447.jpg",
                "abs": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-external-oblique-external-oblique-157612399.jpg",
                "shoulders": "https://thumbs.dreamstime.com/b/deltoid-d-rendered-muscle-illustration-157612398.jpg",
                "quads": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-vastus-lateralis-vastus-lateralis-157612633.jpg",
                "traps": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-trapezius-trapezius-157612310.jpg",
                "back": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-latissimus-dorsi-latissimus-dorsi-157612158.jpg",
                "triceps": "https://thumbs.dreamstime.com/b/triceps-d-rendered-muscle-illustration-157612423.jpg",
                "calves": "https://thumbs.dreamstime.com/b/gastrocnemius-d-rendered-muscle-illustration-157612044.jpg",
                "hamstrings": "https://thumbs.dreamstime.com/b/biceps-femoris-longus-d-rendered-muscle-illustration-157611954.jpg",
                "glutes": "https://thumbs.dreamstime.com/b/d-rendered-muscle-illustration-gluteus-maximus-gluteus-maximus-157612061.jpg"}]

muscle_numbers = {"biceps": "1",
                    "shoulders": "2",
                    "chest": "4",
                    "triceps": "5",
                    "calves": "7",
                    "glutes": "8",
                    "traps": "9",
                    "quads": "10",
                    "hamstrings": "11",
                    "back": "12",
                    "abs": "14"}


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

        db.session.add(new_user)
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

def add_comment():
    form = CommentForm()

    form.validate_on_submit()
    name = form.name.data
    title = form.title.data
    content = form.content.data
    date_posted = form.date_posted.data
    workout_id = form.workout_id.data

    comment = Comments(name = name, title = title, content = content, date_posted = date_posted, workout_id = workout_id)

    db.session.add(comment)
    db.session.commit()

    
    return redirect(request.url)



# @app.route('/<muscle>')
# def specific_workouts(muscle):
#     """Show the workouts that are offered for the muscle selected"""
#     muscle = muscle_numbers['chest']
#     workout = make_api_request(muscle)
#     workouts = workout['results']
#     comment = Comments.query.all()
#     form = CommentForm()
#     return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)





@app.route('/chest')
def chest_workouts():
    """show the chest workouts that are offered"""
    workout = make_api_request('4')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/chest', methods = ["POST"])
def add_chest_comment():
    """Show the comment form"""

    add_comment()
    return redirect(request.url)


@app.route('/biceps')
def bicep_workouts():
    """show the biceps workouts that are offered"""
    workout = make_api_request('1')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)


@app.route('/biceps', methods = ["POST"])
def add_bicep_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)


@app.route('/abs')
def ab_workouts():
    """show the ab workouts that are offered"""
    workout = make_api_request('14')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/abs', methods = ["POST"])
def add_abs_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/shoulders')
def shoulder_workouts():
    """show the shoulder workouts that are offered"""
    workout = make_api_request('2')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)


@app.route('/shoulders', methods = ["POST"])
def add_shoulders_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/traps')
def trap_workouts():
    """show the trap workouts that are offered"""
    workout = make_api_request('9')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/traps', methods = ["POST"])
def add_traps_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/quads')
def quad_workouts():
    """show the quad workouts that are offered"""
    workout = make_api_request('10')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/quads', methods = ["POST"])
def add_quads_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/back')
def back_workouts():
    """show the back workouts that are offered"""
    workout = make_api_request('12')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/back', methods = ["POST"])
def add_back_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/triceps')
def tricep_workouts():
    """show the triceps workouts that are offered"""
    workout = make_api_request('5')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/triceps', methods = ["POST"])
def add_triceps_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/calves')
def calf_workouts():
    """show the calf workouts that are offered"""
    workout = make_api_request('7')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/calves', methods = ["POST"])
def add_calf_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/hamstrings')
def hamstring_workouts():
    """show the hamstring workouts that are offered"""
    workout = make_api_request('11')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/hamstrings', methods = ["POST"])
def add_hamstring_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

@app.route('/glutes')
def glute_workouts():
    """show the glute workouts that are offered"""
    workout = make_api_request('8')
    workouts = workout['results']
    comment = Comments.query.all()
    form = CommentForm()
    return render_template("muscles/workout.html", workouts = workouts, form = form, comment = comment)

@app.route('/glutes', methods = ["POST"])
def add_glute_comment():
    """Show the comment form"""
    add_comment()
    return redirect(request.url)

