import pandas as pd
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from src.app.core.database import get_paid_status, load_history, get_roommates, save_tracker, clear_db

history = Blueprint('history', __name__)

@history.route('/history')
def index():
    if "user_id" not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    billing_history = load_history(user_id)
    
    if not billing_history.empty:
        names = get_roommates(user_id)
        month_displays = calculate_monthly_data(user_id, billing_history, names)
        month_displays.reverse() 
    else:
        month_displays = []

    return render_template('history.html', month_displays=month_displays)

@history.route('/update_payment', methods=['POST'])
def update_payment():
    user_id = session['user_id']
    month = request.form.get('month')
    names = get_roommates(user_id)
    full_member_list = ["Me"] + names
    
    updated_rows = []
    for name in full_member_list:
        # check if checkbox was clicked
        is_paid = request.form.get(f"paid_{month}_{name}") == 'on'
        updated_rows.append({
            "Roommate Name": name,
            "Paid": is_paid,
            "Current Month Split": float(request.form.get(f"split_{month}_{name}")),
            "Rollover Amount": float(request.form.get(f"rollover_{month}_{name}")),
            "Total Owed": float(request.form.get(f"total_{month}_{name}"))
        })
    
    df = pd.DataFrame(updated_rows)
    save_tracker(user_id, df, month)
    
    flash(f"Updated payments for {month}", "success")
    return redirect(url_for('history.history_page'))

@history.route('/clear_history', methods=['POST'])
def clear_history():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        clear_db(user_id)
        flash("All billing and payment history has been cleared.", "success")
    except Exception as e:
        flash(f"Error clearing database: {e}", "danger")
        
    return redirect(url_for('history.history_page'))

def calculate_monthly_data(user_id, billing_history, names):
    unique_months = billing_history["Billing Month"].unique()
        
    months_ascending = sorted(
        unique_months,
        key=lambda date_str: pd.to_datetime(date_str, format='%B %Y'),
    )
    
    full_member_list = ["Me"] + names
    running_rollover = {name: 0.0 for name in full_member_list}
    month_displays = []
    
    for month in months_ascending:
        month_df = billing_history[billing_history["Billing Month"] == month]
        monthly_total = month_df["Total Amount Due"].sum()
        num_ppl = len(full_member_list)
        monthly_split = round(monthly_total / num_ppl, 2) if num_ppl > 0 else 0
        paid_dict = get_paid_status(user_id, month)
        
        roommates = pd.DataFrame({
            "Roommate Name": full_member_list,
            "Current Month Split": monthly_split,
            "Rollover Amount": [running_rollover[name] for name in full_member_list],
            "Paid": [bool(paid_dict.get(name, False)) for name in full_member_list]
        })
        
        roommates["Total Owed"] = (roommates["Current Month Split"] + roommates["Rollover Amount"]).round(2)
        roommates = roommates[["Roommate Name", "Current Month Split", "Rollover Amount", "Total Owed", "Paid"]]
        
        for idx, row in roommates.iterrows():
            name = row["Roommate Name"]
            if not row["Paid"]:
                # if they did not pay carry the balance into the next month
                running_rollover[name] = row["Total Owed"]
            else:
                running_rollover[name] = 0.0
        
        month_displays.append({
            "month": month,
            "df": month_df,
            "roommates": roommates,
            "monthly_total": monthly_total,
            "monthly_split": monthly_split
        })
    
    return month_displays