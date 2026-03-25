from flask import Blueprint, render_template, session, redirect, url_for

landing = Blueprint('landing', __name__)

@landing.route('/')
def index():
    if "user_id" in session:
        return redirect(url_for('dashboard.index'))
        
    return render_template('landing.html')