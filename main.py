from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Todo
from forms import RegisterForm, LoginForm, TodoForm
import os

app = Flask(__name__)

# SECRET_KEY: Used for session encryption and CSRF token generation
# WHY: Without this, Flask-Login sessions and WTForms CSRF fail
# Production: Use environment variable, never hardcode
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# SQLAlchemy database URI
# sqlite:///: Relative path protocol for SQLite
# instance/ folder: Flask convention for instance-specific files (database, config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'

# Suppresses warning about event system (not needed for this app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db.init_app: Connects SQLAlchemy instance to Flask app
# WHY separate: Allows factory pattern (multiple apps with same models)
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)  # Connects LoginManager to app
login_manager.login_view = 'login'  # Redirect here if @login_required fails
# login_message: Flash message when redirected (Bootstrap alert will display this)
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login callback: Loads user from database using ID stored in session

    WHEN CALLED: Every request where user logged in
    HOW IT WORKS:
    1. Flask-Login stores user_id in session cookie (encrypted with SECRET_KEY)
    2. On each request, Flask-Login calls this function with that user_id
    3. Returns User object, becomes available as current_user throughout request

    db.session.get(Model, id): SQLAlchemy method replacing deprecated Query.get()
    """
    return db.session.get(User, int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET request: Display empty form
    POST request: Process form submission

    HTTP methods:
    - GET: Retrieve data, no side effects (idempotent)
    - POST: Submit data, causes changes (non-idempotent)
    """
    form = RegisterForm()

    # validate_on_submit(): Returns True only if:
    # 1. Request method is POST
    # 2. CSRF token valid
    # 3. All field validators pass
    if form.validate_on_submit():
        # form.email.data: Validated, sanitized data from form field
        # .filter_by: SQLAlchemy query method (generates SELECT WHERE)
        # .first(): Returns first result or None
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            # flash(): Stores message in session for next request
            # 'danger': Bootstrap alert class (red warning)
            flash('Email already registered', 'danger')
            # redirect: Sends HTTP 302 response with Location header
            # url_for('register'): Generates URL from route function name
            # WHY url_for: URLs stay correct if route path changes
            return redirect(url_for('register'))

        # Create new User instance (in memory, not yet in database)
        user = User(email=form.email.data)
        user.set_password(form.password.data)  # Hashes password

        # db.session.add: Stages object for database INSERT
        db.session.add(user)
        # db.session.commit: Executes SQL transaction, writes to database
        # WHY separate: Can add multiple objects then commit once (atomic transaction)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')  # Green alert
        return redirect(url_for('login'))

    # GET request or validation failed: render form with errors
    # form.errors: Dictionary of {field_name: [error_messages]}
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Check user exists AND password correct
        # WHY separate checks: Don't reveal which failed (security)
        if user and user.check_password(form.password.data):
            # login_user: Flask-Login function
            # 1. Stores user.id in encrypted session cookie
            # 2. Sets current_user to this User object
            # remember=form.remember.data: Creates persistent cookie (stays after browser close)
            login_user(user, remember=form.remember.data)

            # request.args.get('next'): URL parameter for redirect after login
            # Example: /todos?next=/add redirects to /add after successful login
            # WHY: User clicked protected link → redirected to login → login → back to original link
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required  # Decorator: Redirects to login if current_user not authenticated
def logout():
    """
    logout_user: Flask-Login function
    - Removes user_id from session
    - Sets current_user to AnonymousUserMixin (is_authenticated=False)
    """
    logout_user()
    flash('You have been logged out', 'info')  # Blue alert
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Main page: Display todos and handle new todo creation

    DATA FLOW:
    1. User submits form → POST request with form data
    2. Flask receives request.form data
    3. TodoForm(request.form) creates form instance
    4. form.validate_on_submit() checks POST + CSRF + validators
    5. If valid: Create Todo, add to database, commit
    6. redirect() sends 302 response → browser makes new GET request
    7. GET request: Query todos from database
    8. render_template() generates HTML with todos
    9. Browser receives HTML, displays page
    """
    form = TodoForm()

    if form.validate_on_submit():
        # Create Todo instance with current_user.id (provided by Flask-Login)
        # current_user: Proxy object that's the User returned by load_user()
        todo = Todo(
            content=form.content.data,
            user_id=current_user.id  # Links todo to logged-in user
        )
        db.session.add(todo)
        db.session.commit()

        # POST-Redirect-GET pattern: Prevents duplicate submissions on refresh
        # WHY: Browser refresh repeats last request. If last request was POST,
        # form resubmits. Redirect makes last request GET (safe to repeat).
        return redirect(url_for('index'))

    # Query todos for current user only
    # .filter_by(user_id=current_user.id): WHERE user_id = ?
    # .all(): Returns list of Todo objects
    todos = Todo.query.filter_by(user_id=current_user.id).all()

    # Passes variables to template as keyword arguments
    # Template accesses as {{ form }}, {{ todos }}
    return render_template('index.html', form=form, todos=todos)


@app.route('/toggle/<int:todo_id>')
@login_required
def toggle(todo_id):
    """
    <int:todo_id>: URL parameter converter
    - Matches only integers in URL
    - Converts to Python int
    - Passes as function argument

    Example URL: /toggle/5 → todo_id = 5
    """
    # db.session.get(Model, id): Fetch by primary key
    # .get_or_404(): Returns object or 404 error if not found
    todo = db.session.get(Todo, todo_id)

    if not todo:
        flash('Todo not found', 'danger')
        return redirect(url_for('index'))

    # Security check: Verify todo belongs to current user
    # WHY: User could manually type /toggle/999 for someone else's todo
    if todo.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    # Toggle boolean
    todo.completed = not todo.completed
    # No db.session.add needed - object already tracked by session
    # WHY: Object came from database query, SQLAlchemy tracks changes automatically
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/delete/<int:todo_id>')
@login_required
def delete(todo_id):
    todo = db.session.get(Todo, todo_id)

    if not todo:
        flash('Todo not found', 'danger')
        return redirect(url_for('index'))

    if todo.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    # db.session.delete: Stages object for DELETE
    db.session.delete(todo)
    db.session.commit()

    flash('Todo deleted', 'success')
    return redirect(url_for('index'))


# Application context: Creates database tables if they don't exist
# with app.app_context(): Pushes Flask app context (required for db operations outside routes)
# db.create_all(): Checks models, creates missing tables
# WHY here: Runs once on app start, before first request
# Production: Use migrations (Flask-Migrate/Alembic) instead
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # debug=True: Auto-reloads on code changes, shows detailed errors
    # Production: debug=False (security risk to show errors publicly)
    app.run(debug=True)