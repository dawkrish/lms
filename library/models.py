from library import db

class User(db.Model):
     __tablename__ = "USER"
     id = db.Column(db.Integer, primary_key = True, autoincrement = True)
     username = db.Column(db.String, nullable = False, unique = True)
     email = db.Column(db.String, nullable = False, unique = True)
     password = db.Column(db.String, nullable = False)
     is_admin = db.Column(db.Boolean, default=False)

class Book(db.Model):
     __tablename__ = "BOOK"
     id = db.Column(db.Integer, primary_key = True, autoincrement = True)
     name = db.Column(db.String, nullable = False)
     author = db.Column(db.String, nullable = False)
     content = db.Column(db.Text, nullable = False)
     date_issued = db.Column(db.DateTime)
     return_date = db.Column(db.DateTime)

class Section(db.Model):
     __tablename__ = "SECTION"
     id = db.Column(db.Integer, primary_key = True, autoincrement = True)
     name = db.Column(db.String, nullable = False)
     description =  db.Column(db.Text, nullable = False)
     date_created = db.Column(db.DateTime, nullable = False)

class Issue(db.Model):
     __tablename__ = "ISSUE"
     id = db.Column(db.Integer, primary_key = True, autoincrement = True)
     user_id = db.Column(db.Integer, db.ForeignKey('USER.id'), nullable = False)
     book_id = db.Column(db.Integer, db.ForeignKey('BOOK.id'), nullable = False)
     date_issued = db.Column(db.DateTime, db.ForeignKey('BOOK.date_issued'), nullable = False)
     return_date = db.Column(db.DateTime, db.ForeignKey('BOOK.return_date'), nullable = False)

