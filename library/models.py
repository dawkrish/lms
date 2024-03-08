from library import db


class User(db.Model):
    __tablename__ = "USER"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    issues = db.Relationship('Issue', backref="user_issues", cascade="all, delete")


class Book(db.Model):
    __tablename__ = "BOOK"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('SECTION.id'), nullable=False)

    issues = db.Relationship('Issue', backref="book_issues", cascade="all, delete")

    def __repr__(self) -> str:
        return f"--{self.id}\t{self.name}\t{self.author}--"


class Section(db.Model):
    __tablename__ = "SECTION"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)

    books = db.Relationship('Book', backref="section_books", cascade="all, delete")



class Issue(db.Model):
    __tablename__ = "ISSUE"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating = db.Column(db.Integer, default=0)
    active_status = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('USER.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('BOOK.id'), nullable=False)
    date_issued = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"--{self.id}\t{self.active_status}\t{self.book_id}--"
