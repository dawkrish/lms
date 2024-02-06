from re import error
from flask import Flask,request, render_template, redirect, session
import bcrypt
from library import app, db, models


'''
    HOME
'''

@app.route("/")
def index():
    return render_template("home.html")

'''
    USER
'''

@app.route("/user/signup", methods=["GET","POST"])
def user_signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("user_signup.html",error="Passwords do not match")
            
        if models.User.query.filter(models.User.username== username).first() is not None:
            print("username already exists")
            return render_template("user_signup.html",error="Username already exists")
        
        if models.User.query.filter(models.User.email == email).first() is not None:
            print("email already exists")
            return render_template("user_signup.html",error="Email already exists")

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(15))
        new_user = models.User(username=username, email=email, password=hashed_password.decode())
        db.session.add(new_user)
        db.session.commit()

        return redirect("/user/login")
    return render_template("user_signup.html")


@app.route("/user/login",methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = models.User.query.filter(models.User.username== username).first() 
        if existing_user is None:
            return render_template("user_login.html",error="Invalid credentials")
        if not bcrypt.checkpw(password.encode(), existing_user.password.encode()):
            return render_template("user_login.html",error="Invalid credentials")
            
        session["username"] = existing_user.username
        return redirect("/user/dashboard")

    return render_template("user_login.html")

@app.route("/user/dashboard")
def user_dashboard():
    # we need to send all the books that this user has issued...
    return render_template("user_dashboard.html")
    

'''
    ADMIN
'''

@app.route("/admin/login",methods=["GET","POST"])
def admin_login():
    '''
        We have assumed admin's email to be 'admin@library.com'
        We have assumed admin's password to be 'admin_password'
        We can change it as we want.
    '''
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_admin = models.User.query.filter(models.User.email == email).first()
        if existing_admin is None:
            return render_template("admin_login.html",error="This email does not exists")
        if existing_admin.is_admin is False:
            return render_template("admin_login.html", error="This is not the admin-email")
        if not bcrypt.checkpw(password.encode(), existing_admin.password.encode()):
            return render_template("admin_login.html", error="This is not the admin-password")

        session["username"] = existing_admin.username
        return redirect("/admin/dashboard")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    # all the issued books, by the user
    return render_template("admin_dashboard.html")

'''
    LIBRARY
'''
@app.route("/library")
def library():
    books = models.Book.query.filter().all()
    print(books)
    return "helo"
@app.route("/issue/")
def book():
    issues = models.Issue.query.filter().all()
    print(issues)
    return "helo"
@app.route("/section")
def section():
    return
