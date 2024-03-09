import datetime

import bcrypt
from flask import request, render_template, redirect, session

from library import app, db, models

'''
    HOME
'''


@app.route("/")
def index():
    if session.get('username') is None:
        return render_template("index.html")
    if session.get("username") == "admin":
        return redirect("/admin/dashboard")
    else:
        return redirect("/user/dashboard")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username")
    return redirect("/")


'''
    USER
'''


@app.route("/user/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("user_signup.html", error="Passwords do not match")

        if models.User.query.filter(models.User.username == username).first() is not None:
            return render_template("user_signup.html", error="Username already exists")

        if models.User.query.filter(models.User.email == email).first() is not None:
            return render_template("user_signup.html", error="Email already exists")

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(15))
        new_user = models.User(
            username=username, email=email, password=hashed_password.decode())
        db.session.add(new_user)
        db.session.commit()

        return redirect("/user/login")
    return render_template("user_signup.html")


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        return render_template("user_login.html")

    username = request.form["username"]
    password = request.form["password"]
    if username == "admin":
        return render_template("admin_not_allowed.html")

    existing_user = models.User.query.filter(
        models.User.username == username).first()
    if existing_user is None:
        return render_template("user_login.html", error="Invalid credentials")
    if not bcrypt.checkpw(password.encode(), existing_user.password.encode()):
        return render_template("user_login.html", error="Invalid credentials")

    session["username"] = existing_user.username
    return redirect("/user/dashboard")


@app.route("/user/dashboard")
def user_dashboard():
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") == "admin":
        return render_template("admin_not_allowed.html")

    username = session.get("username")
    user_id = get_user_id()
    existing_user = models.User.query.filter(
        models.User.username == username).first()

    issue_records = models.Issue.query.filter(
        models.Issue.user_id == user_id, models.Issue.active_status == True).all()
    modified_issue_records = []

    for ir in issue_records:
        modified_issue_records.append(modify_the_issue_record(ir))

    data = {
        "user": existing_user,
        "issued_books": modified_issue_records,
    }
    return render_template("user_dashboard.html", data=data)


@app.route("/user/<id>", methods=["GET", "POST"])
def user_profile(id):
    if session.get("username") is None:
        return render_template("no_login.html")

    username = session.get("username")
    existing_user = models.User.query.get(id)

    if int(id) == 1:
        return redirect("/admin/dashboard")

    if existing_user is None:
        data = {
            "type": "User"
        }
        return render_template("not_found.html", data=data)

    issue_records = models.Issue.query.filter(
        models.Issue.user_id == id, models.Issue.active_status == True).all()
    modified_issue_records = []

    for ir in issue_records:
        modified_issue_records.append(modify_the_issue_record(ir))
    data = {
        "user": existing_user,
        "logged_in_user": username,
        "issued_books": modified_issue_records,
        "error": ""
    }
    if request.method == "GET":
        return render_template("user_profile.html", data=data)

    updated_username = request.form["updated_username"]
    updated_email = request.form["updated_email"]
    current_password = request.form["current_password"]
    updated_password = request.form["updated_password"]
    updated_confirm_password = request.form["updated_confirm_password"]

    if models.User.query.filter(models.User.username == updated_username).first() is not None:
        data = {
            "user": existing_user,
            "logged_in_user": username,
            "error": "This username is already used, try another"
        }
        return render_template("user_profile.html", data=data)

    if models.User.query.filter(models.User.email == updated_email).first() is not None:
        data = {
            "user": existing_user,
            "logged_in_user": username,
            "error": "This email is already used, try another"
        }
        return render_template("user_profile.html", data=data)

    if not bcrypt.checkpw(current_password.encode(), existing_user.password.encode()):
        data = {
            "user": existing_user,
            "logged_in_user": username,
            "error": "The current password is incorrect"
        }
        return render_template("user_profile.html", data=data)

    if updated_password != updated_confirm_password:
        data = {
            "user": existing_user,
            "logged_in_user": username,
            "error": "The updated password and updated confirm password does not match"
        }
        return render_template("user_profile.html", data=data)

    existing_user.username = updated_username
    existing_user.email = updated_email
    existing_user.password = bcrypt.hashpw(
        updated_password.encode(), bcrypt.gensalt(10)).decode()

    db.session.commit()
    session["username"] = existing_user.username
    data = {
        "user": existing_user,
        "logged_in_user": username,
        "error": ""
    }
    return redirect("/")


'''
    ADMIN
'''


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """
        We have assumed admins email to be 'admin@library.com'
        We have assumed admins password to be 'admin_password'
        We can change it as we want.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_admin = models.User.query.filter(
            models.User.email == email).first()
        if existing_admin is None:
            return render_template("admin_login.html", error="This email does not exists")
        if existing_admin.is_admin is False:
            return render_template("admin_login.html", error="This is not the admin-email")
        if not bcrypt.checkpw(password.encode(), existing_admin.password.encode()):
            return render_template("admin_login.html", error="This is not the admin-password")

        session["username"] = existing_admin.username
        return redirect("/admin/dashboard")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") != "admin":
        return render_template("user_not_allowed.html")

    sections = models.Section.query.filter().all()
    books = models.Book.query.filter().all()

    modified_books = []
    for b in books:
        modified_books.append(modify_the_book(b))

    issue_records = models.Issue.query.filter().all()
    modified_issue_records = []
    for ir in issue_records:
        modified_issue_records.append(modify_the_issue_record(ir))
    data = {
        "sections": sections,
        "books": modified_books,
        "issue_records": modified_issue_records,
    }
    return render_template("admin_dashboard.html", data=data)


'''
    LIBRARY
'''


@app.route("/library", methods=["GET", "POST"])
def library():
    if session.get("username") is None:
        return render_template("no_login.html")

    all_books = models.Book.query.filter().all()
    if request.method == "GET":
        non_issued_books = []
        for b in all_books:
            if not get_book_status(b):
                non_issued_books.append(b)

        grouped_books = group_books(non_issued_books)
        modified_group_books = []
        for gb in grouped_books:
            modified_group_books.append(modify_the_book(gb))
        sections = models.Section.query.filter().all()

        data = {
            "books": modified_group_books,
            "sections": sections,
            "current_section_name": "all",
        }
        return render_template("library.html", data=data)

    section_name = request.form["section_name"]
    if section_name == "all":
        non_issued_books = []
        for b in all_books:
            if not get_book_status(b):
                non_issued_books.append(b)

        grouped_books = group_books(non_issued_books)
        modified_group_books = []
        for gb in grouped_books:
            modified_group_books.append(modify_the_book(gb))

    else:
        section_id = models.Section.query.filter(
            models.Section.name == section_name).first().id
        section_books = models.Book.query.filter(
            models.Book.section_id == section_id).all()

        non_issued_books = []
        for b in section_books:
            if not get_book_status(b):
                non_issued_books.append(b)

        grouped_books = group_books(non_issued_books)
        modified_group_books = []
        for gb in grouped_books:
            modified_group_books.append(modify_the_book(gb))

    sections = models.Section.query.filter().all()
    data = {
        "books": modified_group_books,
        "sections": sections,
        "current_section_name": section_name,
    }
    return render_template("library.html", data=data)


'''
    BOOK
'''


@app.route("/book/<id>")
def book_get(id):
    if session.get("username") is None:
        return render_template("no_login.html")
    existing_book = models.Book.query.get(id)
    if existing_book is None:
        data = {
            "type": "Book"
        }
        return render_template("not_found.html", data=data)
    issue_records = models.Issue.query.filter(models.Issue.book_id == id).all()
    book_copies = models.Book.query.filter(models.Book.name == existing_book.name,
                                           models.Book.author == existing_book.author).all()
    data = {
        "book": modify_the_book(existing_book),
        "book_copies": book_copies,
        "issue_records": [modify_the_issue_record(ir) for ir in issue_records]
    }

    return render_template("book_get.html", data=data)


@app.route("/create_book", methods=["POST"])
def book_post():
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") != "admin":
        return render_template("user_not_allowed.html")

    if request.method == "POST":
        if session.get("username") != "admin":
            return "<h1>You are not admin! You can't create books </html>"

        book_name = request.form["book_name"]
        book_author = request.form["book_author"]
        book_content = request.form["book_content"]
        book_section = request.form["book_section"]
        book_copies = request.form["book_copies"]

        for i in range(int(book_copies)):
            new_book = models.Book(
                name=book_name, author=book_author, content=book_content, section_id=book_section)
            db.session.add(new_book)
            db.session.commit()
        return redirect("/admin/dashboard")


@app.route("/book/update/<id>", methods=["GET", "POST"])
def book_update(id):
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") != "admin":
        return render_template("user_not_allowed.html")

    existing_book = models.Book.query.get(id)

    if existing_book is None:
        data = {
            "type": "Book"
        }
        return render_template("not_found.html", data=data)

    modified_book = modify_the_book(existing_book)
    book_copies = models.Book.query.filter(models.Book.name == existing_book.name,
                                           models.Book.author == existing_book.author).all()
    if request.method == "GET":
        data = {
            "sections": models.Section.query.filter().all(),
            "book": modified_book,
            "book_copies": book_copies,
        }
        return render_template("book_update.html", data=data)

    updated_book_name = request.form["updated_book_name"]
    updated_book_author = request.form["updated_book_author"]
    updated_book_content = request.form["updated_book_content"]
    updated_book_section = request.form["updated_book_section"]
    if len(book_copies) > 1:
        multiple_bool = request.form["multiple_bool"]

        if multiple_bool == "yes":
            for i in book_copies:
                i.name = updated_book_name
                i.author = updated_book_author
                i.content = updated_book_content
                i.section = updated_book_section
                db.session.commit()

        else:
            existing_book.name = updated_book_name
            existing_book.author = updated_book_author
            existing_book.content = updated_book_content
            existing_book.section = updated_book_section
            db.session.commit()
    else:
        existing_book.name = updated_book_name
        existing_book.author = updated_book_author
        existing_book.content = updated_book_content
        existing_book.section = updated_book_section
        db.session.commit()
    return redirect("/admin/dashboard")


@app.route("/book/delete/<id>", methods=["GET", "POST"])
def book_delete(id):
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") != "admin":
        return render_template("user_not_allowed.html")

    existing_book = models.Book.query.get(id)
    if existing_book is None:
        data = {
            "type": "Book"
        }
        return render_template("not_found.html", data=data)

    book_copies = models.Book.query.filter(models.Book.name == existing_book.name,
                                           models.Book.author == existing_book.author).all()
    if request.method == "GET":
        data = {
            "book": modify_the_book(existing_book),
            "book_copies": book_copies
        }
        return render_template("book_delete.html", data=data)

    if len(book_copies) > 1:
        multiple_bool = request.form["multiple_bool"]
        if multiple_bool == "yes":
            for i in book_copies:
                db.session.delete(i)
                db.session.commit()
        else:
            db.session.delete(existing_book)
            db.session.commit()
    else:
        db.session.delete(existing_book)
        db.session.commit()
    return redirect("/admin/dashboard")


@app.route("/book/issue/<id>", methods=["GET", "POST"])
def book_issue(id):
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") == "admin":
        return render_template("admin_not_allowed.html")

    existing_book = models.Book.query.get(id)
    if existing_book is None:
        data = {
            "type": "Book"
        }
        return render_template("not_found.html", data=data)

    if get_book_status(existing_book) is True:
        return '''
            <h1>This book is already issued </h1>
            <p> Go back to library  <a href="/library">click here</a></p>
        '''

    user_id = get_user_id()
    today_date = datetime.date.today()
    issue_records = models.Issue.query.filter(
        models.Issue.user_id == user_id, models.Issue.active_status == True).all()
    total_number_of_books_issued = len(issue_records)

    if total_number_of_books_issued >= 5:
        return '''
            <h2>You have already issued 5 books, return a book to issue new one !</h2>
            <a href="/user/dashboard">Click here</a>
        '''

    if request.method == "GET":
        modified_book = modify_the_book(existing_book)

        last_date = today_date + datetime.timedelta(days=7)
        min_date = str(today_date)
        max_date = str(last_date)

        data = {
            "book": modified_book,
            "min_date": min_date,
            "max_date": max_date
        }
        return render_template("book_issue.html", data=data)

    if request.method == "POST":
        return_date = request.form["return_date"]

        year = return_date[:4]
        month = return_date[5:7]
        if month[0] == '0':
            month = month[1]
        day = return_date[8:]
        if day[0] == '0':
            day = day[1]

        year, month, day = int(year), int(month), int(day)
        py_return_date = datetime.date(year, month, day)

        new_issue = models.Issue(active_status=True, user_id=user_id, book_id=id, date_issued=today_date,
                                 return_date=py_return_date)
        db.session.add(new_issue)
        db.session.commit()

        return redirect("/user/dashboard")


@app.route("/book/return/<id>", methods=["GET", "POST"])
def book_return(id):
    if session.get("username") is None:
        return render_template("no_login.html")

    '''
    Note that admins are allowed to "return" [revoke] the books, that's why the below 2 lines
    are commented, but not in <book_issue>
    
    # if session.get("username") != "admin":
    #    return render_template("user_not_allowed.html")
    '''

    existing_book = models.Book.query.get(id)
    if existing_book is None:
        data = {
            "type": "Book"
        }
        return render_template("not_found.html", data=data)

    if get_book_status(existing_book) is False:
        return '''
        <h1>This book is not issued, so it cannot be returned </h1>
        <p> Go back to library  <a href="/library">click here</a></p>
        '''

    issue_record = models.Issue.query.filter(
        models.Issue.book_id == id, models.Issue.active_status == True).first()
    
    if session["username"] == "admin":
        issue_record.rating = -1
        issue_record.active_status = False
        issue_record.return_date = datetime.date.today()
        db.session.commit()
        return redirect("/admin/dashboard")
    
    if issue_record.user_id != get_user_id():
        return '''
            <h1>This book is not issued by you</h1>
            <p><a href="/">Go Back</a></p>
            '''

    if request.method == "GET":
        modified_book = modify_the_book(existing_book)
        data = {
            "book": modified_book,
        }
        return render_template("book_return.html", data=data)

    rating = request.form["rating"]
    issue_record.rating = rating
    issue_record.active_status = False
    issue_record.return_date = datetime.date.today()

    db.session.commit()
    return redirect("/user/dashboard")


'''
    SECTION
'''


@app.route("/section/<id>")
def section_get(id):
    if session.get("username") is None:
        return render_template("no_login.html")
    section = models.Section.query.get(id)
    if section is None:
        data = {
            "type": "Section"
        }
        return render_template("not_found.html", data=data)
    issue_records = models.Issue.query.filter(
        models.Book.section_id == id).all()

    data = {
        "section": section,
        "issue_records": [modify_the_issue_record(ir) for ir in issue_records]
    }

    return render_template("section_get.html", data=data)


@app.route("/create_section", methods=["POST"])
def section_post():
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") != "admin":
        return render_template("user_not_allowed.html")

    if request.method == "POST":
        section_name = request.form["section_name"]
        section_description = request.form["section_description"]
        date_created = datetime.date.today()

        if models.Section.query.filter(models.Section.name == section_name).first() is not None:
            return '''
                This section already exists
                <a href="/admin/dashboard">Go Back</a>
            '''
        new_section = models.Section(
            name=section_name, description=section_description, date_created=date_created)
        db.session.add(new_section)
        db.session.commit()
        return redirect("/admin/dashboard")


@app.route("/section/update/<id>", methods=["GET", "POST"])
def section_update(id):
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") != "admin":
        return render_template("user_not_allowed.html")

    existing_section = models.Section.query.get(id)
    if existing_section is None:
        data = {
            "type": "Section"
        }
        return render_template("not_found.html", data=data)

    if request.method == "GET":
        data = {
            "section": existing_section,
        }
        return render_template("section_update.html", data=data)

    updated_section_name = request.form["updated_section_name"]
    updated_section_description = request.form["updated_section_description"]

    if models.Section.query.filter(models.Section.name == updated_section_name).first() is not None:
        return '''
                This section already exists
                <a href="/admin/dashboard">Go Back</a>
            '''
    existing_section.name = updated_section_name
    existing_section.description = updated_section_description
    db.session.commit()

    return redirect("/admin/dashboard")


@app.route("/section/delete/<id>", methods=["GET", "POST"])
def delete_section(id):
    if session.get("username") is None:
        return render_template("no_login.html")

    if session.get("username") != "admin":
        return render_template("user_not_allowed.html")

    existing_section = models.Section.query.get(id)
    if existing_section is None:
        data = {
            "type": "Section"
        }
        return render_template("not_found.html", data=data)

    if request.method == "GET":
        data = {
            "section": existing_section
        }
        return render_template("section_delete.html", data=data)

    db.session.delete(existing_section)
    db.session.commit()
    return redirect("/admin/dashboard")


'''
    UTILITY FUNCTIONS
'''


def modify_the_issue_record(issue_record):
    b = models.Book.query.get(issue_record.book_id)
    s = models.Section.query.get(b.section_id)
    u = models.User.query.get(issue_record.user_id)
    modified_issue_record = {
        "issue_id": issue_record.id,
        "book_id": b.id,
        "user_id": u.id,
        "username": u.username,
        "name": b.name,
        "author": b.author,
        "content": b.content,
        "section_name": s.name,
        "date_issued": issue_record.date_issued,
        "status": issue_record.active_status,
        "rating": issue_record.rating,
        "return_date": issue_record.return_date
    }
    return modified_issue_record


def modify_the_book(book):
    s = models.Section.query.get(book.section_id)
    modified_book = {
        "id": book.id,
        "name": book.name,
        "author": book.author,
        "section_name": s.name,
        "content": book.content,
        "total_rating": calculate_book_rating(book.id)
    }

    return modified_book


def get_user_id():
    user = models.User.query.filter(
        models.User.username == session.get("username")).first()
    if user is None:
        return None
    return user.id


def get_book_status(b):
    issue_record = models.Issue.query.filter(
        models.Issue.book_id == b.id).all()
    for ir in issue_record:
        if ir.active_status:
            return True
    return False


def group_books(books):
    grouped_books = []
    for b in books:
        isbn = f'{b.name}{b.author}'
        check = False
        for gb in grouped_books:
            gb_isbn = f'{gb.name}{gb.author}'
            if gb_isbn == isbn:
                check = True
                break
        if not check:
            grouped_books.append(b)
    return grouped_books


def calculate_book_rating(b_id):
    b = models.Book.query.get(b_id)
    book_copies = models.Book.query.filter(
        models.Book.name == b.name, models.Book.author == b.author).all()
    total_rating = 0
    for bc in book_copies:
        issue_records = models.Issue.query.filter(
            models.Issue.book_id == bc.id, models.Issue.rating > 1).all()
        for ir in issue_records:
            total_rating += ir.rating

    return total_rating
