
from flask import render_template
from flask import redirect, request
from flask import current_app as app
from flask import g 
from flask import session
from flask_login import LoginManager, current_user, login_user, login_required
from application.models import *
from datetime import date,datetime

login = LoginManager()
login.init_app(app)
login.login_view = 'login'

@app.route('/', methods=['GET', 'POST'])
def welcome():
    #solely made to redirect to the login page
    return redirect('login')

@login.user_loader
def load_user(username):
    #here we load the users using the user_loader 
    return User.query.get(username)
    #takes in user_id and it returns the actual object from sqlalchemy
    #this object represents user row in the db table 

@app.route('/register', methods=['GET','POST'])
def register():
    #registering new user 
    if request.method == 'POST':
        #sign in validation
        if len(request.form['password']) == 0:
            error = 'Please fill in the password'

        elif len(request.form['password']) < 8:
            error = 'Your password needs to be a little longer, try again.'
            return render_template('register.html', error=error)

        if request.form['password'] != request.form['repeat']:
            error = "Passwords don't match :( "
            return render_template('register.html', error=error)

        new_user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    elif request.method == 'GET':
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #registered users login page 
    #login validation
    if request.method == 'POST':
        if len(request.form['password']) < 8:
            error = 'Your password needs to be atleast 8 character long, try again.'
            return render_template('login.html', error=error)
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        #validation
        if user is None:
            error = "Make sure you get the username and password right :("
            return render_template('login.html', error=error)
        login_user(user)
        return redirect("/main")
    elif request.method == 'GET':
        return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    #Log users out
    session.pop('logged_in', None)
    return redirect('login')

@app.route('/main', methods=["GET", "POST"])
@login_required
#by decorating a view with this, we ensure that the current user is logged in/ authenticated.
def home():
    #adding lists to the cards
    g.user = current_user
    tasks = None
    error = None
    data = [{'status':'backlog'},
            {'status':'todo'},
            {'status':'doing'},
            {'status':'done'}]
    deadline = request.form.get('deadline')
    today = date.today()
    d = today.strftime("%d/%m/%Y")

    if request.form:
        try:
            # A task/list can get into a card only if its unique
            if request.form.get("title") in [task.title for task in Task.query.all()]:
                error = "Please fill in a new task :)"
            else:
                if request.form.get('deadline'):
                    #task id=1 because autoincrementing ID would be harder to keep track of 
                    task = Task(title=request.form.get("title"), status=request.form.get("status"), user_id = g.user.id,deadline=deadline)  
                    ftdDateList = deadline.split('-')
                    ftdDate = date(int(ftdDateList[0]),int(ftdDateList[1]),int(ftdDateList[2]))
                else:
                    task = Task(title=request.form.get("title"), status=request.form.get("status"), user_id = g.user.id)
                tasks = Task.query.all()
                if request.form.get('status'):

                    db.session.add(task)
                    db.session.commit()
                else:
                    error='Please select status'

        except Exception as e:
            error=e
    #tasks are selected based on the status select form 
    
    tasks = Task.query.filter_by(user_id=g.user.id).all()
    backlog = Task.query.filter_by(status='backlog',user_id=g.user.id).all()
    todo = Task.query.filter_by(status='todo',user_id=g.user.id).all()
    doing = Task.query.filter_by(status='doing',user_id=g.user.id).all()
    done = Task.query.filter_by(status='done',user_id=g.user.id).all()
    
    return render_template("home.html", error=error, tasks=tasks,backlog=backlog, todo=todo, doing=doing, done=done,data=data, myuser=current_user,today=d)

@app.route("/update", methods=["POST"])
def update():
   #lists within the cards can move with the update function
    
    try:
        newstatus = request.form.get("newstatus")
        name = request.form.get("name")
        task = Task.query.filter_by(title=name).first()
        task.status = newstatus
        #updating the status in database
        db.session.commit()
    except Exception as e:
        print("This task status failed to update")
        print(e)
    return redirect("/main")

@app.route("/delete", methods=["POST"])
def delete():
    #Deleting tasks/lists
    title = request.form.get("title")
    task = Task.query.filter_by(title=title).first()
    #Deleting from database
    db.session.delete(task)
    db.session.commit()
    return redirect("/main")

@app.route("/summary", methods=["GET","POST"])
def summary():
    g.user = current_user
    today = datetime.today()
    failed = []
    success = []
    backlog = Task.query.filter_by(status='backlog',user_id=g.user.id).all()
    todo = Task.query.filter_by(status='todo',user_id=g.user.id).all()
    done = Task.query.filter_by(status='done',user_id=g.user.id).all()
    doing = Task.query.filter_by(status='doing',user_id=g.user.id).all()

    '''
      If deadline of a certain task has passed, it doesn't matter what card the task is in.
      It will still be counted as a failure.
      Only if deadline of a task is in within deadline and it is in the "done" card, it will be counted
      as a success.  
    '''

    #deadline is compared with the current date 
    for i in done:
        if i.deadline:
            #date is stored in db as a string so i need to convert it back to date to compare
            strToDate = datetime.strptime(i.deadline,"%Y-%m-%d") 
            if strToDate > today:
                success.append(i.title)
        
    for j in todo:
        if j.deadline:
            strToDate = datetime.strptime(j.deadline,"%Y-%m-%d")
            if today > strToDate:
                failed.append(j.title)

    for k in backlog:
        if k.deadline:
            strToDate = datetime.strptime(k.deadline,"%Y-%m-%d")
            if today > strToDate:
                failed.append(k.title)

    for m in doing:
        if m.deadline:
            strToDate = datetime.strptime(m.deadline,"%Y-%m-%d")
            if today > strToDate:
                failed.append(m.title)

    successNum = len(success)
    failedNum = len(failed)

    return render_template('summary.html',todo=todo, successNum=successNum, failedNum=failedNum,success=success,failed=failed)