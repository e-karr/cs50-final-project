from flask import flash, g, redirect, render_template, request, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth.routes import login_required
from app.extensions import db
from app.models.account import Account
from app.models.player import Player
from app.models.team import Team
from app.user import bp

@bp.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    """Show user profile"""

    # get logged in user id
    user = g.user
    history = None
    error = None

    try:
        # get registration history
        history = user.get_registration_history(db.session)
    except Exception as e:
            print(f"Error: {e}")
            error = "An error occured while getting registration history"
            db.session.rollback()
    
    if error:
        flash(error, 'error')

    return render_template("user/profile.html", user=user, history=history)


@bp.route("/update", methods=("GET", "POST"))
@login_required
def update():
    """Update account information"""

    # Get current user information
    user = g.user

    if request.method == "GET":
        return render_template("user/update.html", user=user)

    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")
    gender = request.form.get("gender")
    error = None

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
    
    if error is None:
        try:
            # Update account information, if necessary
            if first_name != user.first_name:
                user.update_first_name(first_name, db.session)

            if last_name != user.last_name:
                user.update_last_name(last_name, db.session)

            if phone_number != user.phone_number:
                user.update_phone_number(phone_number, db.session)

            if email != user.email:
                user.update_email(email, db.session)

            if gender != user.gender:
                user.update_gender(gender, db.session)

            flash("You have successfully updated your contact information.", "success")
            return redirect(url_for('user.profile'))
        except Exception as e:
            print(f"Error: {e}")
            error = "An error occured while updating contact information"
            db.session.rollback()
    
    flash(error, "error")

    return redirect(url_for('user.update'))

@bp.route("/password", methods=("GET", "POST"))
@login_required
def password():
    """Change Password"""

    # User reaches page via GET
    if request.method == "GET":
        return render_template("user/password.html")
    
    # Get current user information
    user = g.user

    # User reaches page via POST
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")
    error = None

    if not old_password:
        error = "Must enter current password."
    if not new_password:
        error = "Must enter new password."
    if not confirmation:
        error = "Must confirm new password."
    if not check_password_hash(user.password_hash, old_password):
        error = "Invalid current password."
    if new_password and confirmation:
        error = Account.validate_password(new_password, confirmation)

    if error is None:
        try:
            
                user.update_password(generate_password_hash(new_password), db.session)
                flash("You have successfully updated your password.", "success")
                return redirect(url_for('user.profile'))
        except Exception as e:
                print(f"Error: {e}")
                error = "An error occured while updating password"
                db.session.rollback()

    flash(error, "error")
    return redirect(url_for('user.password'))

@bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = g.user
    error = None
    is_captain = (db.session.query(Player.captain, Team.team_name)
                            .join(Team)
                            .filter(Player.player_id == user.id)
                            .all())

    for i in is_captain:
        if i[0] == "Yes":
            error = f"Must designate alternative captain for {i[1]} before deleting account."
            break

    if error is None:
        try:
            
            user.delete_account(db.session)
            flash("Your account was successfully deleted.", "success")
            session.clear()
            return redirect(url_for('main.index'))
        except Exception as e:
                print(f"Error: {e}")
                error = "An error occured while deleting account"
                db.session.rollback()

    flash(error, 'error')
    return redirect(url_for('user.profile'))

