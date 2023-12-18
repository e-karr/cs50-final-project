from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required
from .models.account import Account


bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    from .db import db
    """Show user profile"""

    # get logged in user id
    user= g.user

    # get registration history
    history = user.get_registration_history(db.session)

    # get team rosters
    for team in history:
        team.players = team.get_roster(db.session)

    return render_template("user/profile.html", id=user.id, user=user, history=history)


@bp.route("/update", methods=("GET", "POST"))
@login_required
def update():
    from .db import db
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

    # check phone number for only digits
    if not phone_number.isdigit():
        error = "Phone number must only contain numbers."

    if error is None:
        try:
            # Update account information, if necessary
            if first_name != user.first_name:
                Account.update_first_name(user.id, first_name, db.session)

            if last_name != user.last_name:
                Account.update_last_name(user.id, last_name, db.session)

            if phone_number != user.phone_number:
                Account.update_phone_number(user.id, phone_number, db.session)

            if email != user.email:
                Account.update_email(user.id, email, db.session)

            if gender != user.gender:
                Account.update_gender(user.id, gender, db.session)

            flash("You have successfully updated your contact information.", "success")
            return redirect(url_for('user.profile'))
        except Exception as e:
            print(f"Error: {e}")
            error = "An error occured while updating contact information"
            db.session.rollback()
        finally:
            db.session.close()
    
    flash(error, "error")

    return render_template("user/update.html", user=user)

# TODO user change password
# @app.route("/password", methods=["GET", "POST"])
# @login_required
# def password():
#     """Change Password"""

#     # User reaches page via GET
#     if request.method == "GET":
#         return render_template("password.html")

#     # User reaches page via POST
#     old_password = request.form.get("old_password")
#     new_password = request.form.get("new_password")
#     confirmation = request.form.get("confirmation")

#     old_hash = db.execute("""SELECT password_hash 
#                              FROM accounts WHERE id = ?""", 
#                              session["user_id"])

#     special_characters = ['$', '#', '@', '!', '*']

#     if not old_password:
#         flash("Must enter current password.", "error")
#         return redirect("/password")

#     if not new_password:
#         flash("Must enter new password.", "error")
#         return redirect("/password")

#     if not confirmation:
#         flash("Must confirm new password.", "error")
#         return redirect("/password")

#     # Validate password inputs
#     if not check_password_hash(old_hash[0]["password_hash"], old_password):
#         flash("Invalid current password.", "error")
#         return redirect("/password")

#     if new_password != confirmation:
#         flash("New passwords don't match.", "error")
#         return redirect("/password")

#     if len(new_password) < 8:
#         flash("Password must be at least 8 characters.", "error")
#         return redirect("/password")

#     if not any(i.isdigit() for i in new_password):
#         flash("Password must contain at least one number.", "error")
#         return redirect("/password")

#     if not any(j.isupper() for j in new_password):
#         flash("Password must contain at least one capital letter.", "error")
#         return redirect("/password")

#     if not any(k in special_characters for k in new_password):
#         flash("Password must contain at least one special character ($, #, @, !, *).", "error")
#         return redirect("/password")

#     db.execute("""UPDATE accounts 
#                   SET password_hash = ? 
#                   WHERE id = ?""", 
#                   generate_password_hash(new_password), session["user_id"])

#     flash("Your password has been successfully updated.", "success")
#     return redirect("/profile")

# TODO delete account
# @app.route("/delete_account", methods=["POST"])
# @login_required
# def delete_account():

#     captain = db.execute("""SELECT captain, team_name 
#                             FROM registered_players 
#                             INNER JOIN teams ON teams.id = registered_players.team_id 
#                             WHERE player_id = ?""", 
#                             session["user_id"])

#     for i in captain:
#         if i["captain"] == "Yes":
#             flash("Must designate alternative captain for %s before deleting account." % (i["team_name"]), "error")
#             return redirect("/profile")

#     db.execute("DELETE FROM accounts WHERE id = ?", session["user_id"])

#     flash("Your account was successfully deleted.", "success")
#     session.clear()
#     return redirect("/")