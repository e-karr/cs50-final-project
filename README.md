# KVKL Registration Web Application
#### Video Demo: [CS50 Video Demo](https://www.youtube.com/watch?v=aeZm5W6CpK8)

## Table of Contents
* [Introduction](#introduction)
* [Technologies](#technologies)
* [Code Files](#code-files)
* [Features](#features)
* [Status](#status)

# Introduction
This is my final project for Harvard's CS50. It is a registration web application for the [Kaw Valley Kickball League](https://kawvalleykickball.com). The goal is to streamline team and player registration for league events. With the web application, users can create an account, view upcoming events, register a team for an event, and join a team. Users can also view a list of currently registered teams and rosters for each team. Lastly, users can leave a team, de-register an entire team, and/or delete their account.

# Technologies
* Python 3.11
    * cs50 9.2.4
    * Flask 2.2.2
    *  Flask-Login 0.6.2
    *  Flask-Session 0.4.0
    *  Jinja2 3.1.2
    *  Werkzeug 2.2.2
* Bootstrap 5.2
* HTML
* CSS
* Sqlite3 database

# Code Files
* app.py
* kvkl_registration.db
* styles.css
* HTML templates
    * account.html
    * index.html
    * layout.html
    * login.html
    * password.html
    * event_selection.html
    * player_register.html
    * profile.html
    * team_register.html
    * update.html

## app.py
The app.py file contains all the back-end python that allows the web appication to function. The python also queries for data from the sqlite database and adds new data to the database

## kvkl_registration.db
This is the sqlite database that stores the data displayed in the web appication. The database contains four tables. The schema for each table is below.
1. accounts

| Column Name | Data Type | Contraints |
| --- | --- | --- |
| id | INTEGER | NOT NULL PRIMARY KEY AUTOINCREMENT |
| email | TEXT | NOT NULL |
| first_name | TEXT | NOT NULL |
| last_name | TEXT | NOT NULL |
| phone_number | NUMERIC | NOT NULL |
| password_hash | TEXT | NOT NULL |
| gender | TEXT | NOT NULL |

2. events

| Column Name | Data Type | Contraints |
| --- | --- | --- |
| id | INTEGER | NOT NULL PRIMARY KEY AUTOINCREMENT |
| event_name | TEXT | NOT NULL |
| month | TEXT | NOT NULL |
| day | INTEGER | NOT NULL |
| year | YEAR | NOT NULL |
| time | TEXT | NOT NULL |
| number_teams | INTEGER | NOT NULL |
| spots_available | INTEGER | NOT NULL |

3. teams

| Column Name | Data Type | Contraints |
| --- | --- | --- |
| id | INTEGER | NOT NULL PRIMARY KEY AUTOINCREMENT |
| team_name | TEXT | NOT NULL |
| sponsor | TEXT |  |
| event_id | INTEGER | NOT NULL FOREIGN KEY REFERENCES events (id) ON DELETE CASCADE |
| passcode | INTEGER | NOT NULL |

4. registered_players

| Column Name | Data Type | Contraints |
| --- | --- | --- |
| captain | TEXT | NOT NULL |
| player_id | INTEGER | NOT NULL FOREIGN KEY REFERENCES accounts (id) ON DELETE CASCADE |
| team_id | INTEGER | NOT NULL FOREIGN KEY REFERENCES teams (id) ON DELETE CASCADE |
| event_id | INTEGER | NOT NULL FOREIGN KEY REFERENCES events (id) ON DELETE CASCADE |

## styles.css
The CSS file contains a few stylings to personalize the web application outside of Bootstrap. Most styling is done with Bootstrap.

## HTML Templates
The HTML templates are rendered based on which part of the web application to which the user is navigating.

One design choice to note, I had trouble understanding the JavaScript necessary to create dependent drop downs in the "Join a Team" form. To get around that, when clicking "Join a Team", the user is directed to the "event_selection.html" page. Once an event is selected in the first drop down, the event is submitted to the app.py backend and the "player_register.html" page is rendered. This second page now has a generated drop down of teams to select from for the selected event and the user can complete the remainder of the form. However, to change the selected event, users must click "Join a Team" in the navigation bar to reset the form. In future iterations of this web application, I plan to utilize JavaScript to make this form more user friendly.

# Features
* Homepage list of upcoming events
* Create an account and login
* View registered teams and team rosters
* Register a team for an event
* Join a currently registered team
* Leave a team or de-register an entire team
* Delete account

## Homepage
The homepage shows a list of upcoming events. Users can create an account, log in, see a list of registered teams, or view team rosters.

![Screenshot of web application homepage with list of upcoming events](/images/homepage.png)

When you click on "Registered Teams", the event will expand to show a list of teams.

![Screenshot of list of registered teams](/images/registered-teams.png)

If you click on "Team Roster", a list of players registered for that team will appear. The roster will also denote who is the captain.

![Screenshot of team roster popup](/images/team-roster.png)

If you click "Sign Up" from the homepage and you're not logged in, a popup will prompt you to either log in or create an account.

![Screenshot of "sign up" popup](/images/team-roster.png)

## Create an Account
Users can use this form to create an account. When submitting the form, the application will check to ensure an account doesn't already exist with the supplied email address.

![Screenshot of "create an account" form](/images/create-account.png)

## Log In
Users can use this page to log into their account.

![Screenshot of log in page](/images/log-in.png)

Once logged in, the homepage will update with a new navigation bar menu and the option to "Register a Team" or "Join a Team" when clicking "Sign Up" on an event.

![Screenshot of logged in navigation bar](/images/nav-bar.png)

![Screenshot of updated "sign up" popup](/images/updated-sign-up.png)

## Profile
A user's profile displays current contact information and a team registration history. If the user is a team captian, the registration history will display the passcode other players need to join that team. Captains can also designate a new captain with the "Update Captain" button or "De-register" an entire team. All users can elect to "Leave" a team they are registered for or view the rosters for each team. The profile also allows users to update contact information, change password, or delete their account.

![Screenshot of profile page](/images/profile.png)

## Join a Team
Users can use the "Join a Team" form to join a team already registered for an event. An event must be selected before a list of teams will be available for selection. The form will autofill contact information for the signed-in user.

![Screenshot of "join a team" form](/images/join-a-team.png)

## Register a Team
Users can use the "Register a Team" form to register a team for an event. Registering a team will then allow additional players to join that team. The user who registers the team will automatically be listed as the team captain. Once the register team form is submitted, a 6-digit passcode is generated for the captain to share with players. The passcode is saved in the captain's profile.

![Screenshot of "register a team" form](/images/register-team.png)

# Status
For the scope of CS50, this project is complete. It is currently only in a development environment. However, for my own personal skill development, I plan to continue working on this registration page and expanding it's functionality. Below are planned updates as I learn new coding skills.

## KVKL Registration 2.0
* Order events by date.
* Events move to a "Previous Events" section once the date has passed
* Add admin account funtionality. The admin can add events and check rosters for eligibility
* Make "Join A Team" page more user friendly with JavaScript
* Add option for users to upload an account profile picture
* Add "date_registered" column to registered_plaers SQL table
    * Profile registration history can then show the date a user registered for an event/team
* Add confirmation emails for creating an account, updating account information, changing password, registering for an event, joining a team, leaving a team, de-registering a team, and deleting account
* Add "forgot password" functionality