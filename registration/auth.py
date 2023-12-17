import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from registration.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/register", methods=("GET", "POST"))
def register():
    """Create a new account"""

    if request.method == "POST":
        # get input from create account form
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        first_name = request.form.get("firstname")
        last_name = request.form.get("lastname")
        phone_number = request.form.get("phonenumber")
        gender = request.form.get("gender")

        special_characters = ['$', '#', '@', '!', '*']

        db = get_db()
        error = None

        # validate form input
        if not first_name:
            error = "Must enter first name"
        elif not last_name:
            error = "Must enter last name"
        elif not phone_number:
            error = "Must enter phone number"
        elif not phone_number.isdigit():
            error = "Phone number must only contain numbers."
        elif not email:
            error = "Must enter an email."
        elif not gender:
            error = "Must select a gender"
        elif not password:
            error = "Must enter a password."
        elif not confirmation:
            error = "Must confirm password."
        elif password != confirmation:
            error = "Passwords don't match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif not any(i.isdigit() for i in password):
            error = "Password must contain at least one number."
        elif not any(j.isupper() for j in password):
            error = "Password must contain at least one capital letter."
        elif not any(k in special_characters for k in password):
            error = "Password must contain at least one special character ($, #, @, !, *)."

        if error is None:
            try:
                db.execute("""INSERT INTO accounts (email, first_name, last_name, phone_number, password_hash, gender) 
                    VALUES (?, ?, ?, ?, ?, ?)""", 
                    (email, first_name, last_name, phone_number, generate_password_hash(password), gender))
            except db.IntegrityError:
                error = f"Email {email} is already registered"
            else:
                # Log new user in
                user = db.execute("SELECT id FROM accounts WHERE email = ?", (email,)).fetchone()
                session["user_id"] = user["id"]
                flash("You have successfully created an account.", "success")
                return redirect(url_for('index'))
        
        flash(error, "error")
    
    return render_template("auth/register.html")
    
@bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST
    if request.method == "POST": 

        # Get input values
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_db()
        error = None

        if not email:
            error = "Please enter an email."
        elif not password:
            error = "Please enter a password."

        # Query database for username
        user = db.execute("SELECT * FROM accounts WHERE email = ?", email,).fetchone()

        # Check for valid email and password
        if user is None:
            error = "Invalid email"
        elif not check_password_hash(user["password_hash"], password):
            error = "Invalid password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            flash("Successful login", "success")
            return redirect(url_for('index'))
        
        flash(error, "error")

    # User reached route via GET
    return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM accounts WHERE id = ?", (user_id,)
        ).fetchone()

@bp.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("You have successfully logged out.", "success")
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def decorated_function(*args, **kwargs):
        if g.User is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return decorated_function
    
    