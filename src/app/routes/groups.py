import json
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from src.app.database import get_user_groups, create_group, add_group_member, get_group_members, get_user_by_email, delete_group, update_group_name, update_member, delete_member

groups = Blueprint('groups', __name__)

@groups.route('/groups')
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    user_groups = get_user_groups(session["user_id"])
    for group in user_groups:
        group['members'] = parse_members(group)
            
    return render_template('groups.html', groups=user_groups)

@groups.route('/groups/create', methods=['POST'])
def create():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    group_name = request.form.get('group_name')
    group_type = request.form.get('group_type', 'group') 
    names = request.form.getlist('new_names[]')
    emails = request.form.getlist('new_emails[]')
    
    if group_type == 'individual' and names:
        group_name = names[0]
    
    if group_name:
        try:
            group_id = create_group(user_id, group_name, group_type)
            process_members(user_id, group_id, names, emails, auto_create_individual=(group_type == 'group'))
            flash(f"Group '{group_name}' created successfully!", "success")
        except Exception as e:
            flash(f"Error creating group: {e}", "danger")
            
    return redirect(url_for('groups.index'))

@groups.route('/groups/edit/<int:group_id>', methods=['POST'])
def edit(group_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    new_name = request.form.get('group_name')
    existing_ids = request.form.getlist('existing_ids[]')
    existing_names = request.form.getlist('existing_names[]')
    existing_emails = request.form.getlist('existing_emails[]')
    new_names = request.form.getlist('new_names[]')
    new_emails = request.form.getlist('new_emails[]')
    
    if new_name:
        try:
            update_group_name(group_id, new_name)
            for m_id, name, email in zip(existing_ids, existing_names, existing_emails):
                clean_name = name.strip()
                clean_email = email.strip()
                if clean_name:
                    update_member(m_id, clean_name, clean_email)

            process_members(user_id, group_id, new_names, new_emails, auto_create_individual=True)
            flash(f"Group '{new_name}' updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating group: {e}", "danger")
            
    return redirect(url_for('groups.index'))

@groups.route('/groups/delete/<int:group_id>', methods=['POST'])
def delete(group_id):
    if "user_id" in session:
        delete_group(group_id, session["user_id"])
        flash("Group deleted.", "info")
    return redirect(url_for('groups.index'))

@groups.route('/groups/members/delete/<int:member_id>', methods=['POST'])
def remove_member(member_id):
    if "user_id" not in session:
        return "Unauthorized", 401
    
    try:
        delete_member(member_id)
        return "Success", 200
    except Exception as e:
        return str(e), 500
    
def parse_members(group):
    """Safely parses members_json from the database result."""
    if not group.get('members_json'):
        return []
    try:
        return json.loads(group['members_json']) if isinstance(group['members_json'], str) else group['members_json']
    except (json.JSONDecodeError, TypeError):
        return []
    
def process_members(user_id, group_id, names, emails, auto_create_individual=False):
    """Cleans and adds new members to a group, optionally ensuring they exist as individuals."""
    for name, email in zip(names, emails):
        clean_name = name.strip()
        clean_email = email.strip() if email else ""
        
        if clean_name:
            add_group_member(group_id, clean_name, clean_email)
            if auto_create_individual:
                ensure_individual_exists(user_id, clean_name, clean_email)

def ensure_individual_exists(owner_id, name, email):
    """Prevents empty-email collisions by falling back to name checks."""
    clean_name = name.strip()
    clean_email = email.strip() if email else ""
    existing_groups = get_user_groups(owner_id)
    
    for group in existing_groups:
        if group.get('group_type') == 'individual':
            members = parse_members(group)
            for m in members:
                if m['role'] == 'owner': 
                    continue
                
                # Match by email if exists, otherwise by name
                if (clean_email and m.get('email') == clean_email) or (not clean_email and m.get('name') == clean_name):
                    return

    new_id = create_group(owner_id, clean_name, 'individual')
    add_group_member(new_id, clean_name, clean_email)