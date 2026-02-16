# Todo List App

A Flask web application with user authentication for managing personal todo lists. Each user has their own secure account and can create, complete, and delete tasks.

## Features

- **User Authentication** – Register and login with email/password
- **Password Security** – Bcrypt hashing with Werkzeug
- **Personal Todo Lists** – Each user sees only their own todos
- **Task Management** – Add, complete/undo, and delete tasks
- **Remember Me** – Persistent login sessions
- **Flash Messages** – User feedback for all actions
- **Responsive Design** – Bootstrap 5 mobile-friendly interface

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing
- **Forms**: WTForms with CSRF protection and validation
- **Frontend**: Bootstrap 5, Jinja2 templates

## Security Features

- Password hashing (pbkdf2:sha256)
- CSRF token protection on all forms
- User authorization checks (users can only modify their own todos)
- Session-based authentication
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Theocrite2/TodoList.git
   cd TodoList
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variable** (optional but recommended)
   ```bash
   # Linux/Mac
   export SECRET_KEY='your-secret-key-here'
   
   # Windows
   set SECRET_KEY=your-secret-key-here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the app**
   ```
   http://localhost:5000
   ```

## Project Structure

```
TodoList/
├── templates/
│   ├── base.html           # Base template with navbar and flash messages
│   ├── register.html       # User registration form
│   ├── login.html          # User login form
│   └── index.html          # Main todo list page
├── main.py                 # Flask application and routes
├── models.py               # SQLAlchemy database models
├── forms.py                # WTForms form definitions
├── requirements.txt        # Python dependencies
└── instance/
    └── todos.db           # SQLite database (auto-created)
```

## Routes

| Route | Methods | Description | Auth Required |
|-------|---------|-------------|---------------|
| `/register` | GET, POST | User registration | No |
| `/login` | GET, POST | User login | No |
| `/logout` | GET | User logout | Yes |
| `/` | GET, POST | View todos & add new todo | Yes |
| `/toggle/<id>` | GET | Toggle todo completion | Yes |
| `/delete/<id>` | GET | Delete a todo | Yes |

## Database Models

### User
- `id` (Integer, Primary Key)
- `email` (String, Unique, Required)
- `password` (String, Hashed, Required)
- `todos` (Relationship to Todo)

### Todo
- `id` (Integer, Primary Key)
- `content` (String, Max 200 chars, Required)
- `completed` (Boolean, Default: False)
- `user_id` (Foreign Key to User)

## Form Validation

### RegisterForm
- Email: Required, valid email format
- Password: Required, minimum 6 characters
- Confirm Password: Must match password field

### LoginForm
- Email: Required, valid email format
- Password: Required
- Remember Me: Optional boolean

### TodoForm
- Content: Required, maximum 200 characters

## Usage

1. **Register**: Create a new account with email and password
2. **Login**: Access your personal todo list
3. **Add Todo**: Enter task in the input field and click "Add Todo"
4. **Complete Todo**: Click "Complete" button (task gets strikethrough)
5. **Undo Todo**: Click "Undo" to mark as incomplete
6. **Delete Todo**: Click "Delete" button with confirmation
7. **Logout**: Click "Logout" in navbar

## Development Notes

- Database created automatically on first run (`instance/todos.db`)
- Debug mode enabled by default (disable for production)
- SECRET_KEY uses environment variable or falls back to dev key
- Password hashing uses Werkzeug's `generate_password_hash()`
- Cascade delete: Deleting a user removes all their todos

## Production Deployment

For production use:

1. Set strong `SECRET_KEY` environment variable
2. Change `debug=False` in `main.py`
3. Use PostgreSQL instead of SQLite
4. Use Flask-Migrate for database migrations
5. Serve with production WSGI server (Gunicorn, uWSGI)
6. Add email verification for registration
7. Implement password reset functionality

## License

MIT
