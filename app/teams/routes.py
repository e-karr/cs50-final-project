from sqlalchemy import select
from app.teams import bp
from flask import (
    flash, g, redirect, render_template, request, url_for,
)
from random import randint
from app.auth.routes import login_required
from app.extensions import db
from app.models.event import Event
from app.models.account import Account
from app.models.team import Team
from app.models.player import Player

@bp.route("/team_register", methods=("GET", "POST"))
@login_required
def team_register():
    """Register a new team"""

    user = g.user

    # User reached route via GET
    if request.method == "GET":
        events = Event.query.all()
        return render_template("team/team_register.html", events=events, user=user)

    #User reached route via POST

    # Generate random 6-digit passcode
    passcode = randint(100000, 999999)
    event_id = request.form.get("event")
    team_name = request.form.get("teamname")
    sponsor = request.form.get("sponsor")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")
    error = None

    if event_id:
        event_id = int(event_id)
        existing_team = Team.query.filter_by(team_name=team_name, event_id=event_id).first()
        selected_event = Event.query.filter_by(id=event_id).first()
        already_registered = Player.query.filter_by(player_id=user.id, event_id=event_id).first()

    # Validate form inputs
    if not event_id:
        error = "Must select an event."
    if not team_name:
        error = "Must enter a team name."
    if not first_name:
        error = "Must enter a first name."
    if not last_name:
        error = "Must enter a last name."
    if not phone_number:
        error = "Must enter a phone number."
    else:
        error = Account.validate_phone_number(phone_number)
    if not email:
        error = "Must enter an email."
    if existing_team:
        error = f"This team is already registered for {selected_event.event_name}"
    if already_registered:
        error = f"You are already registered for {selected_event.event_name}"
    
    if error == None:
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

            # Insert into teams database
            team = Team(
                team_name=team_name,
                sponsor=sponsor,
                event_id=event_id,
                passcode=passcode
            )
            db.session.add(team)
            db.session.commit()

            # update spots available
            selected_event.update_spots_available('subtract', db.session)

            # Add captain to registered_players
            player = Player(
                captain="Yes",
                player_id=user.id,
                team_id=team.id,
                event_id=event_id
            )
            db.session.add(player)
            db.session.commit()
            
            flash(f"You have successfully registered your team. Your team passcode is {passcode}.", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            print(f"Error: {e}")
            error = "An error occured while registering a team."
            db.session.rollback()

    flash(error, 'error')
    return redirect(url_for('teams.team_register'))

@bp.route("/player_register", methods=("GET", "POST"))
@login_required
def player_register():
    """Join a team after selecting an event"""
   
    # Select contact info from logged in user
    user = g.user
    error = None
    # User reached route via GET
    if request.method == "GET":

        events_teams = (db.session.query(Event.event_name,
                                         Team.team_name,
                                         Team.id)
                                    .join(Team, Team.event_id == Event.id)
                                    .all())

        return render_template("team/player_register.html", events=events_teams, user=user)

    # User reached route via POST

    # Validate form inputs
    team_id = request.form.get("team")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")
    passcode = request.form.get("passcode")
    captain = request.form.get("captain")

    if not team_id:
        error = "Must select a team."
    if not first_name:
        error = "Must enter a first name."
    if not last_name:
        error = "Must enter a last name."
    if not phone_number:
        error = "Must enter a phone number."
    else:
        error = Account.validate_phone_number(phone_number)
    if not email:
        error = "Must enter an email."
    if not passcode:
        error = "Must enter a passcode."
    elif len(passcode) != 6:
        error = "Passcode must be 6 digits"
    if not captain:
        error = "Must indicate captain status."

    # Get team passcode
    if error == None:
        team_id = int(team_id)
        event_id = db.session.execute(select(Team.event_id)
                                      .where(Team.id == team_id)).scalar()
        event_name = db.session.execute(select(Event.event_name)
                                      .where(Event.id == event_id)).scalar()
        passcode = int(passcode)
        selected_team = db.session.get(Team, team_id)
        existing_player = db.session.execute(select(Player)
                                             .where(Player.player_id == user.id)
                                             .where(Player.team_id == team_id)).fetchone()
        existing_event = db.session.execute(select(Player)
                                             .where(Player.player_id == user.id)
                                             .where(Player.event_id == event_id)).fetchone()

        if passcode != selected_team.passcode:
            error = "Invalid passcode."
        if existing_player:
            error = f"You are already registered for {selected_team.team_name}."
        if existing_event:
            error = f"You are already registered for {event_name}"

    # Update account information, if necessary
    if error == None:
        try:
            if first_name != user.first_name:
                user.update_first_name(first_name, db.session)

            if last_name != user.last_name:
                user.update_last_name(last_name, db.session)

            if phone_number != user.phone_number:
                user.update_phone_number(phone_number, db.session)

            if email != user.email:
                user.update_email(email, db.session)

            # Update registered_players
            player = Player(
                        captain=captain,
                        player_id=user.id,
                        team_id=team_id,
                        event_id=selected_team.event_id
                    )
            db.session.add(player)
            db.session.commit()

            flash(f"You have successfully registered for {selected_team.team_name}.", "success")
            return redirect(url_for("user.profile"))
        except Exception as e:
            print(f"There was an error: {e}")
            error = f"There was an error registering you for {selected_team.team_name}"
            db.session.rollback()
    
    flash(error, "error")
    return redirect(url_for("teams.player_register"))

@bp.route("/leave_team", methods=["POST"])
@login_required
def leave_team():
    """Leave team"""
    user = g.user
    team_id = int(request.form.get("leave"))
    error = None

    try:

        team_name = db.session.execute(select(Team.team_name)
                                    .where(Team.id == team_id)).scalar()

        is_captain = (db.session.execute(select(Player.captain)
                                        .where(Player.player_id == user.id)
                                        .where(Player.team_id == team_id))).scalar()
        
        if is_captain == "Yes":
            error = f"Must designate alternative captain for {team_name} before leaving team."
        
        if error == None:
            db.session.query(Player).filter_by(team_id=team_id, player_id=user.id).delete()
            db.session.commit()

            flash(f"You have successfully left {team_name}.", "success")

    except Exception as e:
        print(f"There was an error: {e}")
        error = "There was an error processing your request"
        db.session.rollback()

    if error:
        flash(error, "error")
    
    return redirect(url_for('user.profile'))

@bp.route("/de-register_team", methods=["POST"])
@login_required
def deregister_team():
    """De-Register Team"""

    team_id = int(request.form.get("de-register"))
    error = None

    try:

        team = db.session.get(Team, team_id)
        
        event = db.session.query(Event).filter_by(id=team.event_id).first()
        
        db.session.query(Team).filter_by(id=team_id).delete()

        # Delete team roster from registered_players table
        db.session.query(Player).filter_by(team_id=team_id).delete()

        db.session.commit()

        # Update spots_available in events table
        event.update_spots_available('add', db.session)

        flash(f"You have successfully de-registered {team.team_name}.", "success")
    except Exception as e:
        print(f"There was an error: {e}")
        error = "There was an error processing your request"
        db.session.rollback()

    if error:
        flash(error, "error")
    
    return redirect(url_for('user.profile'))


@bp.route("/update_captain", methods=["POST"])
@login_required
def update_captain():
    """Update Captain"""
    user = g.user
    team_id = int(request.form.get("team_id"))
    error = None

    selected_captain = request.form.get("selected_captain")
    print(selected_captain)

    if not selected_captain:
        error = "Must select a new captain."

    if error == None:
        try: 
            # Get team name
            team_id = int(team_id)
            team = db.session.get(Team, team_id)

            current_captain = db.session.query(Player).filter_by(team_id=team_id, player_id=user.id).first()
            
            # Update old captain in registered players table
            current_captain.update_captain_status('No', db.session)

            # Update new captain in registered players table
            new_captain_id = int(selected_captain)
            new_captain = db.session.query(Player).filter_by(team_id=team_id, player_id=new_captain_id).first()
            new_captain.update_captain_status('Yes', db.session)

            flash(f"You have successfully updated the captain for {team.team_name}.", "success")
        except Exception as e:
            print(f"There was an error: {e}")
            error = "There was an error updating the captain"
            db.session.rollback()

    if error:
        flash(error, "error")

    return redirect(url_for('user.profile'))