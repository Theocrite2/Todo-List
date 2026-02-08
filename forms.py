from flask_wtf import FlaskForm  # Base class providing CSRF protection
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# DataRequired, Email, etc. are validator classes that run when form.validate() called


class RegisterForm(FlaskForm):
    """
    FlaskForm: Renders HTML, validates data, handles errors
    Each field is a class attribute becoming HTML <input> when rendered
    """
    # StringField: Renders <input type="text">
    # validators=[]: List of validator instances checked on form.validate()
    email = StringField('Email', validators=[
        DataRequired(),  # Checks field not empty
        Email()  # Checks valid email format with regex
    ])

    # PasswordField: Renders <input type="password"> (hidden characters)
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)  # Minimum 6 characters
    ])

    # EqualTo('password'): Checks this field matches 'password' field
    # WHY: Prevents typos in password registration
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    # SubmitField: Renders <input type="submit">
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # BooleanField: Renders <input type="checkbox">
    # Used for Flask-Login's remember_me feature
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class TodoForm(FlaskForm):
    # Length(max=200): Matches database column size, prevents truncation errors
    content = StringField('Todo', validators=[
        DataRequired(),
        Length(max=200, message='Todo must be less than 200 characters')
    ])
    submit = SubmitField('Add Todo')