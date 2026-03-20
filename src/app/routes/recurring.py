from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from src.app.database import (
    get_user_groups, 
    get_recurring_expenses, 
    add_recurring_expense, 
    delete_recurring_expense,
    update_recurring_expense
)

recurring = Blueprint('recurring', __name__)

@recurring.route('/recurring')
def recurring_page():
    if "user_id" not in session:
        return redirect(url_for('auth.login_page'))
    
    user_id = session['user_id']
    user_groups = get_user_groups(user_id)
    
    # 1. Get the group_id from the URL. Use None as default instead of 0.
    group_id = request.args.get('group_id', type=int)

    # 2. If it is the first time visiting (None) and user has groups, default to the first group.
    # If the user explicitly clicked "All" (0), this block will be skipped.
    if group_id is None and user_groups:
        group_id = user_groups[0]['group_id']
    elif group_id is None:
        group_id = 0 # Default to All if they have no groups yet
        
    # 3. Correct the function call to pass both user_id and group_id
    expenses = get_recurring_expenses(user_id, group_id)
    
    return render_template('recurring.html', 
                           expenses=expenses, 
                           groups=user_groups, 
                           selected_group_id=group_id)

@recurring.route('/recurring/add', methods=['POST'])
def add():
    if "user_id" not in session:
        return redirect(url_for('auth.login_page'))
        
    group_id = request.form.get('group_id', type=int)
    name = request.form.get('expense_name')
    amount = float(request.form.get('amount', 0))
    day = request.form.get('billing_day', type=int)
    
    if name and amount > 0:
        add_recurring_expense(session['user_id'], group_id, name, amount, day)
        flash(f"Added recurring expense: {name}", "success")
        
    return redirect(url_for('recurring.recurring_page', group_id=group_id))

@recurring.route('/recurring/edit/<int:recurring_id>', methods=['POST'])
def edit(recurring_id):
    group_id = request.form.get('group_id')
    name = request.form.get('expense_name')
    amount = float(request.form.get('amount'))
    day = request.form.get('billing_day', type=int)
    
    update_recurring_expense(recurring_id, name, amount, day)
    flash("Subscription updated.", "success")
    return redirect(url_for('recurring.recurring_page', group_id=group_id))

@recurring.route('/recurring/delete/<int:recurring_id>', methods=['POST'])
def delete(recurring_id):
    group_id = request.form.get('group_id')
    delete_recurring_expense(recurring_id)
    flash("Subscription removed.", "info")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"status": "success"})
    
    return redirect(url_for('recurring.recurring_page', group_id=group_id))