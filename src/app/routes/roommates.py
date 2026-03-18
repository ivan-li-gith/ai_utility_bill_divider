from flask import Blueprint, render_template, request, session, redirect, url_for
from src.app.core.database import get_roommates, add_roommate, remove_roommate

roommates = Blueprint('roommates', __name__)

@roommates.route('/roommates')
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    roommates_list = get_roommates(user_id)
    return render_template('roommates.html', roommates=roommates_list)

@roommates.route('/add_roommate', methods=['POST'])
def add_roommate():
    user_id = session.get('user_id')
    name = request.form.get('name')
    if name:
        add_roommate(user_id, name)
        
    return redirect(url_for('roommates.index'))

@roommates.route('/delete_roommate/<name>')
def delete_roommate(name):
    user_id = session.get('user_id')
    remove_roommate(user_id, name)
    return redirect(url_for('roommates.index'))