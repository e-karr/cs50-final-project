from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import Account, Event, Team, Player, db
from .auth import login_required

bp = Blueprint('user', __name__, url_prefix='/user')

# TODO user profile
@bp.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    """Show user profile"""

    # get logged in user id
    user= g.user

    # get registration history
    history = user.get_registration_history(db.session)

    # get team rosters
    for team in history:
        team.players = team.get_roster(db.session)

    return render_template("user/profile.html", id=user.id, user=user, history=history)


# TODO user update profile
# @app.route("/update", methods=["GET", "POST"])
# @login_required
# def update():
#     """Update account information"""

#     # Get current user information
#     user = db.execute("""SELECT * 
#                          FROM accounts 
#                          WHERE id = ?""", 
#                         session["user_id"])

#     # User reaches page via GET
#     if request.method == "GET":
#         return render_template("update.html", user=user)

#     # User reaches page via POST

#     first_name = request.form.get("firstname")
#     last_name = request.form.get("lastname")
#     phone_number = request.form.get("phonenumber")
#     email = request.form.get("email")
#     gender = request.form.get("gender")

#     # Update account information, if necessary
#     if first_name != user[0]["first_name"]:
#         db.execute("""UPDATE accounts 
#                       SET first_name = ? 
#                       WHERE id = ?""", 
#                     first_name, session["user_id"])

#     if last_name != user[0]["last_name"]:
#         db.execute("""UPDATE accounts 
#                       SET last_name = ? 
#                       WHERE id = ?""", 
#                     last_name, session["user_id"])

#     if phone_number != user[0]["phone_number"]:
#         db.execute("""UPDATE accounts 
#                       SET phone_number = ? 
#                       WHERE id = ?""", 
#                       phone_number, session["user_id"])

#     if email != user[0]["email"]:
#         db.execute("""UPDATE accounts 
#                       SET email = ? 
#                       WHERE id = ?""", 
#                       email, session["user_id"])

#     if gender != user[0]["gender"]:
#         db.execute("""UPDATE accounts 
#                       SET gender = ? 
#                       WHERE id = ?""", 
#                       gender, session["user_id"])

#     flash("You have successfully updated your contact information.", "success")
#     return redirect("/profile")

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