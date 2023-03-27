from cs50 import SQL
from flask import Flask, flash, redirect, render_template, session, request, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import date
from random import randint
import csv
import os

# initialize todays date
today = date.today()

app = Flask(__name__)

# sql  database connection
db = SQL("sqlite:///database.db")

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Generates an apology message whenever an error occurs.
# Copied from CS50 Finance PSET 9 helpers.py.
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Stores the information the user submitted
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("confirmation")
        email = request.form.get("email")
        name = request.form.get("name")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure email was submitted
        elif not request.form.get("email"):
            return apology("must provide email", 400)

        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 400)

        # Checks if both passwords submitted by the user match
        if password != password2:
            return apology("Passwords do not match")

        else:

            # hash the password #
            hashed = generate_password_hash(password)

            # See if username already exists
            users = db.execute("SELECT * FROM users WHERE username = ?", username)
            print(users)

            if len(users):
                return apology("Username already exists, please select another username", 400)

            else:
                # Insert user into the database and redicrects them to the login page
                db.execute("INSERT into users (username, hash, name, email) VALUES(?, ?, ?, ?)", username, hashed, name, email)
                return apology("Thanks for registering, please log in now", 200)

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userid"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# completed logs route, allows user to view all the logs and download their logs in csv format
@app.route("/log", methods=["GET"])
@login_required
def log():

    userId = session.get("user_id")
    date = db.execute("SELECT DATE from LOG where logid = 1")
    logs = db.execute("SELECT * FROM log WHERE userid = ?", userId)
    print(logs)
    return render_template("log.html", logs=logs)

# route once a user has begun updating their diary. only accepts post and renders editdiary.html once the query is completed.
@app.route("/updatediary", methods=["POST"])
@login_required
def updatediary():

    # initialize userid
    userId = session.get("user_id")

    # obtain the details from the submitted form
    form = list(request.form.keys())
    formKey = str(form[0])
    formValue = request.form.get(formKey)

    # obtain the date from the form
    selectedDate = request.form.get("selectedDate")

    # find the task id
    task = db.execute("SELECT * FROM usertasks WHERE taskname = ? AND userid = ?", formKey, userId)
    taskId = task[0]["taskid"]

    # insert into the logs
    db.execute("INSERT INTO log (userid, taskid, comment, taskName, date) VALUES (?, ?, ?, ?, ?)", userId, taskId, formValue, formKey, selectedDate)

    # render the template again with updated values
    logSQL = db.execute("SELECT * FROM log WHERE userid = ? and date = ?", userId, selectedDate)
    logs = {d['taskname']:d['comment'] for d in logSQL}
    tasks = db.execute("SELECT * FROM usertasks WHERE userid = ?", userId)
    return render_template("editdiary.html", logs=logs, tasks=tasks, selectedDate=selectedDate)


# allows user to complete an entry they have previously missed
@app.route("/editdiary", methods=["GET", "POST"])
@login_required
def editdiary():

    # initialize userId
    userId = session.get("user_id")

    # if the user has input a date, view the logs for that date
    if request.method == "POST":
        selectedDate = request.form.get("date")
        logSQL = db.execute("SELECT * FROM log WHERE userid = ? and date = ?", userId, selectedDate)
        logs = {d['taskname']:d['comment'] for d in logSQL}
        tasks = db.execute("SELECT * FROM usertasks WHERE userid = ?", userId)
        return render_template("editdiary.html", logs=logs, tasks=tasks, selectedDate=selectedDate)

    # if no date, view the logs for today and allow them to change to another date
    else:
        selectedDate = today
        logSQL = db.execute("SELECT * FROM log WHERE userid = ? and date = ?", userId, selectedDate)
        logs = {d['taskname']:d['comment'] for d in logSQL}
        tasks = db.execute("SELECT * FROM usertasks WHERE userid = ?", userId)
    return render_template("editdiary.html", logs=logs, tasks=tasks, selectedDate=selectedDate, today=today)


# route for the diary
@app.route("/diary", methods=["GET", "POST"])
@login_required
def diary():

    # initialize userId
    userId = session.get("user_id")

    # if user completes a task, determine the task and prepare the values to insert into the db
    if request.method == "POST":
        form = list(request.form.keys())
        formKey = str(form[0])
        formValue = request.form.get(formKey)

        # query the db to obtain the task
        task = db.execute("SELECT * FROM usertasks WHERE taskname = ? AND userid = ?", formKey, userId)

        # obtain the taskid to insert into the logs table
        taskId = task[0]["taskid"]

        # insert into the logs table
        db.execute("INSERT INTO log (userid, taskid, comment, taskName) VALUES(?, ?, ?, ?)", session.get("user_id"), taskId, formValue, formKey)

    # obtain the tasks that have already been completed by the user today
    logSQL = db.execute("SELECT * FROM log WHERE userid = ? AND date = ?", userId, today)

    # obtain all the daily tasks for the current user
    tasks = db.execute("SELECT * FROM usertasks WHERE userid = ?", userId)

    # obtain the scheduled activities for the user today
    activities = db.execute("SELECT * FROM activities WHERE user_id = ? AND date = ?", userId, today)

    # turn log into a dictionary so it can be viewed on the template
    logs = {d['taskname']:d['comment'] for d in logSQL}

    # render template
    return render_template("diary.html", tasks=tasks, logs=logs, today=today, activities=activities)


# route to view and schedule activities
@app.route("/activities", methods=["GET", "POST"])
@login_required
def activities():

    #initialize userid
    userId = session.get("user_id")

    # if task is submitted, add it to the database
    if request.method == "POST":

        task = request.form.get("task")
        taskDate = request.form.get("date")
        db.execute("INSERT INTO activities (activity_name, user_id, date) VALUES (?, ?, ?)", task, userId, taskDate)

        return redirect("/activities")

    # if just viewing tasks, pull out all tasks so the user can see the list
    activities = db.execute("SELECT * FROM activities WHERE user_id = ?", userId)

    return render_template("activities.html", activities=activities)


#route to add a task for each user
@app.route("/addtask", methods=["GET", "POST"])
@login_required
def addtask():

    # if user submits a task, initialize userid and task name
    if request.method == "POST":
        userid = session.get("user_id")
        task = request.form.get("task")

        # pull out taskList to see if a task with the same name already exists
        taskList = db.execute("SELECT * FROM daily WHERE name = ?", task)

        #if it does not exist, add the task to the task list and also the individuals tasks
        if not taskList:
            db.execute("INSERT INTO daily (name) VALUES (?)", task)
            taskInfo = db.execute("SELECT id FROM daily WHERE name = ?", task)
            taskId = taskInfo[0]["id"]
            db.execute("INSERT INTO usertasks (userid, taskid, taskname) VALUES (?, ?, ?)", userid, taskId, task)

            return redirect("/diary")

        # if it does exist, add the task to the individuals tasks
        else:
            taskInfo = db.execute("SELECT id FROM daily WHERE name = ?", task)
            taskId = taskInfo[0]["id"]
            db.execute("INSERT INTO usertasks (userid, taskid, taskname) VALUES (?, ?, ?)", userid, taskId, task)
            return redirect("/diary")

    return render_template("addtask.html")


# Function to export the logs of the user to a csv file for them to download
@app.route("/export", methods=["GET", "POST"])
@login_required
def export():

    # query the db for the users logs:

    rows = db.execute("SELECT * FROM log WHERE userid = ?", session.get("user_id"))

    # Prepare the filename for the individual user

    user = db.execute("SELECT * FROM users WHERE userid = ?", session.get("user_id"))
    username = str(user[0]["username"])
    random = str(randint(0, 2083210938))

    print(rows)

    columns = rows[0].keys()

    # filename becomes username + the current date and time
    filename = str(username + "_" + random + ".csv")

    # write the sql query to csv
    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    # return the csv to download
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)