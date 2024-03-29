from functools import wraps

from flask import flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.account import Account
from app.extensions import db
from app.auth import bp

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

        error = None
        existing_account = Account.get_user_by_email(db.session, email)

        # validate form input
        if not first_name:
            error = "Must enter first name"
        if not last_name:
            error = "Must enter last name"
        if not phone_number:
            error = "Must enter phone number"
        else:
            error = Account.validate_phone_number(phone_number)
        if not email:
            error = "Must enter an email."
        if not gender:
            error = "Must select a gender"
        if not password:
            error = "Must enter a password."
        if not confirmation:
            error = "Must confirm password."
        if password:
            error = Account.validate_password(password, confirmation)
        if existing_account:
            error = "Email is already taken. Please choose a different email."

        if error is None:
            try:
                account = Account(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    password_hash=generate_password_hash(password),
                    gender=gender
                )
                db.session.add(account)
                db.session.commit()
                flash("You have successfully created an account.", "success")
                return redirect(url_for('auth.login'))
            except Exception as e:
                print(f"Error during registration: {e}")
                error = "An error occurred during registration"
                db.session.rollback()

        flash(error, "error")

    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log user in"""
    # User reached route via POST
    if request.method == "POST":
        # Get input values
        email = request.form.get("email")
        password = request.form.get("password")
        error = None

        if not email:
            error = "Please enter an email."
        if not password:
            error = "Please enter a password."

        if error is None:
            try:
                user = Account.get_user_by_email(db.session, email)

                # Check for valid email and password
                if user is None:
                    error = "Invalid email"
                if not check_password_hash(user.password_hash, password):
                    error = "Invalid password."

                if error is None:
                    session.clear()
                    session["user_id"] = user.id
                    flash("Successful login", "success")
                    return redirect(url_for('main.index'))
            except Exception as e:
                print(f"Error during login: {e}")
                error = "An error occurred during login"

        flash(error, "error")

    return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(Account, user_id)

@bp.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("You have successfully logged out.", "success")
    return redirect(url_for('main.index'))

def login_required(view):
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return decorated_function