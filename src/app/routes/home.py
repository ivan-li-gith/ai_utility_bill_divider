import plotly.express as px
import plotly.io as pio
import pandas as pd
from flask import Blueprint, render_template, session, redirect, url_for, request
from src.app.database import get_user_groups, load_history, get_group_members, get_subscription, load_expense_history
from src.app.routes.utilities import calculate_utilities, get_member_names

home = Blueprint('home', __name__)

@home.route('/home')
def home_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    user_id = session["user_id"]
    user_groups = get_user_groups(user_id)
    
    # Get group_id from URL, or default to 0 (All)
    group_id = request.args.get('group_id', type=int)
    if group_id is None:
        group_id = 0
        
    # Load Utilities History
    billing_history = load_history(user_id, group_id if group_id != 0 else None)
    
    # Initialize variables for the Dashboard
    debtors = []
    total_uncollected = 0.0
    util_total = 0.0
    donut_html = ""
    line_html = "<div class='text-center' style='padding: 2rem; color: #999;'>No collection data available yet.</div>"
    
    # 1. Calculate Utilities Debt & History
    if not billing_history.empty and group_id != 0:
        members = get_group_members(group_id)
        names = get_member_names(user_id, members)
        month_displays = calculate_utilities(user_id, billing_history, names, group_id)
        
        if month_displays:
            current_month = month_displays[-1]
            util_total = current_month["monthly_total"]
            
            # Aggregate "Who Owes Me" for Utilities
            latest_utilities = current_month["roommates"]
            for _, row in latest_utilities.iterrows():
                if row["Roommate Name"] != "Me" and not row["Paid"] and row["Total Owed"] > 0:
                    owed = row["Total Owed"]
                    debtors.append({
                        "name": row["Roommate Name"],
                        "utilities": owed,
                        "subscriptions": 0.0, # Placeholder for next phase
                        "expenses": 0.0,      # Placeholder for next phase
                        "total_owed": owed
                    })
                    total_uncollected += owed
            
            # Generate the new Stacked Bar Chart
            line_html = owed_vs_collected_chart(month_displays)
            
    # 2. Fetch Subscriptions & Expenses for the Donut Chart
    subs = get_subscription(user_id, group_id)
    sub_total = sum(s['amount'] for s in subs) if subs else 0.0
    
    exps = load_expense_history(group_id) if group_id != 0 else []
    exp_total = sum(e['amount'] for e in exps) if exps else 0.0
    
    # Generate the Category Donut Chart
    donut_html = category_donut_chart(util_total, sub_total, exp_total)
            
    return render_template('home.html', 
                           debtors=debtors,
                           total_uncollected=total_uncollected,
                           donut_html=donut_html, 
                           line_html=line_html, 
                           groups=user_groups, 
                           selected_group_id=group_id)    
    
def category_donut_chart(util_total, sub_total, exp_total):
    """Creates a donut chart showing the split between the three major app categories."""
    data = [
        {"Category": "Utilities", "Amount": util_total},
        {"Category": "Subscriptions", "Amount": sub_total},
        {"Category": "One-Off Expenses", "Amount": exp_total}
    ]
    df = pd.DataFrame(data)
    df = df[df["Amount"] > 0] # Remove empty categories
    
    if df.empty:
        return "<div class='text-center' style='padding: 2rem; color: #999;'>No spending data to visualize.</div>"
    
    donut_fig = px.pie(
        df, 
        values='Amount', 
        names='Category', 
        hole=0.4, 
        color_discrete_sequence=['#0d6efd', '#eb4f7a', '#ffc107']
    )
    
    donut_fig.update_traces(textinfo='label+percent', textposition='inside')
    donut_fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
    
    return pio.to_html(donut_fig, full_html=False, include_plotlyjs='cdn')
    
def owed_vs_collected_chart(month_displays):
    """Creates a stacked bar chart showing collection rates over time."""
    data = []
    for m in month_displays:
        df = m["roommates"]
        df_others = df[df["Roommate Name"] != "Me"]
        
        # Sum up what was paid vs what wasn't
        collected = df_others[df_others["Paid"] == True]["Total Owed"].sum()
        uncollected = df_others[df_others["Paid"] == False]["Total Owed"].sum()
        
        data.append({"Month": m["month"], "Amount": collected, "Status": "Collected"})
        data.append({"Month": m["month"], "Amount": uncollected, "Status": "Uncollected"})
        
    trend_df = pd.DataFrame(data)
    
    bar_fig = px.bar(
        trend_df, 
        x="Month", 
        y="Amount", 
        color="Status", 
        barmode="stack",
        color_discrete_map={"Collected": "#198754", "Uncollected": "#dc3545"}
    )
    
    bar_fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
    )
    
    return pio.to_html(bar_fig, full_html=False, include_plotlyjs='cdn')