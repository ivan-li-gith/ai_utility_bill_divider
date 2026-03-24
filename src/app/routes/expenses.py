from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from src.app.core.parser import extract_from_receipt_image
from src.app.database import get_user_groups
from src.app.database import load_expense_history, save_new_expense, delete_expense

expenses = Blueprint('expenses', __name__)

@expenses.route('/expenses')
def index():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session["user_id"]
    user_groups = get_user_groups(user_id)
    
    # NEW LOGIC: Handle filtering by Group
    default_group_id = request.args.get('group_id')
    
    # If no group selected, default to the first group the user has
    if not default_group_id and user_groups:
        default_group_id = user_groups[0]['group_id']
        
    # NEW LOGIC: Load the history for the table
    # Convert default_group_id to int if it's set
    current_history = []
    if default_group_id:
        current_history = load_expense_history(int(default_group_id))
    
    return render_template('expenses.html', 
                           groups=user_groups, 
                           staged_items=session.get('staged_receipt_items'),
                           default_group_id=default_group_id,
                           history=current_history)

@expenses.route('/expenses/upload_receipt', methods=['POST'])
def upload_receipt():
    """Handles AI vision processing for physical receipts."""
    group_id = request.form.get("group_id")
    file = request.files.get('receipt_image')
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.heic')):
        try:
            # 1. Send the image to GPT-4o Vision
            items_list = extract_from_receipt_image(file)
            
            # 2. Stage the extracted items in the session to review
            session['staged_receipt_items'] = items_list
            session['staged_expense_group'] = group_id
            flash("Receipt parsed successfully! Please review the items below.", "success")
        except Exception as e:
            flash(f"Failed to process receipt: {e}", "danger")
            
    return redirect(url_for('activity.index'))

@expenses.route('/expenses/manual_add', methods=['POST'])
def manual_add():
    """Handles manual entry and instantly saves it to DB."""
    if "user_id" not in session: return redirect(url_for('auth.login'))
    
    user_id = session["user_id"]
    group_id = request.form.get("group_id")
    item_name = request.form.get("item_name")
    amount = float(request.form.get("amount", 0))
    date = request.form.get("date") # Assuming we add a date picker
    payer_id = user_id # Assuming owner is the payer for simplicity
    split_method = "even" # Default

    if item_name and amount > 0:
        try:
            # INSTANT SAVE (Instead of staging)
            save_new_expense(group_id, user_id, date, item_name, amount, payer_id, split_method)
            flash(f"'{item_name}' added to ledger.", "success")
        except Exception as e:
            flash(f"Error saving expense: {e}", "danger")
            
    # Redirect back to the index for that specific group
    return redirect(url_for('activity.index', group_id=group_id))

@expenses.route('/expenses/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
    """Deletes an expense and returns the user to the ledger."""
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
        
    try:
        delete_expense(expense_id)
        flash("Expense deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting expense: {e}", "danger")
        
    return redirect(url_for('expenses.index'))