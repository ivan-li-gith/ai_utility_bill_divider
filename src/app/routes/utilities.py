from flask import Blueprint, request, session, redirect, url_for, flash, jsonify
from src.app.services.utility_service import (
    process_uploaded_bills, format_and_save_bills, process_status_update
)

utilities = Blueprint('utilities', __name__)

@utilities.route('/utilities/upload', methods=['POST'])
def upload():
    group_id = request.form.get("group_id")
    files = request.files.getlist('bills')
    
    # Send files to the service layer for processing
    all_bill_data, errors = process_uploaded_bills(files)
    
    for error in errors:
        flash(error, "danger")

    session['staged_bills'] = all_bill_data
    session['staged_group_id'] = group_id
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "success"})
    return redirect(url_for('activity.index', group_id=group_id))

@utilities.route('/utilities/save', methods=['POST'])
def save():
    user_id = session['user_id']
    group_id = session.get('staged_group_id')
    bill_count = int(request.form.get('bill_count', 0))

    try:
        # Pass the form data to the service layer to format and save
        if format_and_save_bills(user_id, group_id, bill_count, request.form):
            session.pop('staged_bills', None) 
            session.pop('staged_group_id', None)
            flash("Bills successfully saved to database!", "success")
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for('utilities.index', group_id=group_id))
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "success"})
    
    return redirect(url_for('activity.index', group_id=group_id))

@utilities.route('/utilities/update_status', methods=['POST'])
def update_status():
    user_id = session['user_id']
    month = request.form.get('month')
    group_id = request.form.get('group_id', type=int)
    
    # Calculate all the new cascading rollovers
    all_updates = process_status_update(user_id, group_id, month, request.form)
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            "status": "success", 
            "updates": all_updates
        })
    
    return redirect(url_for('utilities.index', group_id=group_id))