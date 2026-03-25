from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.app.core.supabase_client import supabase
from src.app.database import get_profile

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response:
                session["user_id"] = response.user.id
                profile = get_profile(response.user.id)
                
                if not profile:
                    return redirect(url_for("setup.setup_page")) 
                return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(f"Login failed: {str(e)}", "danger")
            
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            flash("Check your email for a confirmation link!", "info")
            return redirect(url_for("auth.login_page"))
        except Exception as e:
            flash(f"Signup failed: {str(e)}", "danger")
            
    return render_template('signup.html')

@auth.route('/login/<provider>')
def oauth_login(provider):
    try:
        redirect_url = url_for("auth.oauth_callback", _external=True)
        response = supabase.auth.sign_in_with_oauth({
            "provider": provider, 
            "options": {
                "redirect_to": redirect_url
            }    
        })
        
        return redirect(response.url)
    except Exception as e:
        return f"OAuth sign in failed: {e}"
    
@auth.route('/callback')
def oauth_callback():
    code = request.args.get("code")
    if code:
        try:
            response = supabase.auth.exchange_code_for_session({"auth_code": code})
            session["user_id"] = response.user.id
            profile = get_profile(response.user.id) 
            
            if not profile:
                # NEW: Capture Google data to pre-fill the setup page!
                session['oauth_email'] = response.user.email
                session['oauth_name'] = response.user.user_metadata.get('full_name', '')
                
                flash("Successfully authenticated! Please complete your profile.", "info")
                return redirect(url_for("setup.setup_page"))
            
            # If profile exists, they are an existing user. Skip setup!
            session["user_name"] = profile.get("display_name")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(f"Authentication error: {e}", "danger")
            return redirect(url_for("auth.login_page"))
    return "Missing authorization code", 400

@auth.route('/logout')
def logout():
    supabase.auth.sign_out()
    session.clear()
    return redirect(url_for('auth.login_page'))