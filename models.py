from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()  # SQLAlchemy instance - this object manages all database operations


class User(UserMixin, db.Model):
    """
    UserMixin: Flask-Login class providing is_authenticated, is_active, is_anonymous, get_id()
    db.Model: SQLAlchemy base class that makes this a database table
    """
    __tablename__ = 'users'  # Explicit table name in database

    # db.Column: SQLAlchemy class defining column properties
    # primary_key=True: This column uniquely identifies each row, auto-increments
    id = db.Column(db.Integer, primary_key=True)

    # unique=True: Database constraint preventing duplicate emails
    # nullable=False: Database constraint requiring this field
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # db.relationship: SQLAlchemy relationship, NOT a database column
    # backref='owner': Adds 'owner' attribute to Todo objects for reverse lookup
    # lazy=True: Todos are only loaded from database when accessed (performance)
    # cascade='all, delete-orphan': When user deleted, delete their todos automatically
    todos = db.relationship('Todo', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """
        Werkzeug function: Hashes password with pbkdf2:sha256
        WHY: Never store plaintext passwords. Hash is one-way encryption.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Compares plaintext password against stored hash
        Returns: Boolean - True if match
        """
        return check_password_hash(self.password, password)


class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    # db.Boolean: Stores True/False as 1/0 in database
    # default=False: New todos start incomplete
    completed = db.Column(db.Boolean, default=False, nullable=False)

    # db.ForeignKey: Database constraint linking this to users.id
    # ondelete='CASCADE': If user deleted, database automatically deletes their todos
    # WHY: Maintains referential integrity, prevents orphaned todos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        """String representation for debugging - shows in Python console"""
        return f'<Todo {self.id}: {self.content}>'