from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database.database import *
from src.app.database.group_table import *
from src.app.database.member_table import *
from src.app.database.profile_table import *
from src.app.database.bill_table import *
from src.app.database.payment_table import *

setup = Blueprint('setup', __name__)

@setup.route('/setup')
def index():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
    return render_template('setup.html')

@setup.route('/setup/save', methods=['POST'])
def save():
    user_id = session.get("user_id")
    display_name = request.form.get("display_name")
    age = request.form.get("age")
    group_name = request.form.get("group_name")
    
    try:
        save_profile(user_id, display_name, age)
        session["user_name"] = display_name
        
        if group_name:
            group_id = create_group(user_id, group_name)
            session["active_group_id"] = group_id
            session["active_group_name"] = group_name
            flash(f"Welcome, {display_name}! Your group '{group_name}' is ready.", "success")
        else:
            flash(f"Profile created! Welcome, {display_name}.", "success")
            
        return redirect(url_for('home.index'))
        
    except Exception as e:
        flash(f"An error occurred during setup: {e}", "danger")
        return redirect(url_for('setup.index'))
