from sqlalchemy import text
from .database import get_engine

def add_recurring_expense(user_id, group_id, name, amount, day):
    """Adds a new fixed recurring expense rule including the billing day."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO recurring_expenses (user_id, group_id, expense_name, amount, billing_day)
            VALUES (:uid, :gid, :name, :amount, :day)
        """), {"uid": user_id, "gid": group_id, "name": name, "amount": amount, "day": day})

def get_recurring_expenses(user_id, group_id=None):
    """Fetches recurring expenses. If group_id is 0 or None, fetches all for the user."""
    engine = get_engine()
    
    # JOIN with group_list to get the group_name for the "Charging: X" label
    query_str = """
        SELECT re.recurring_id, re.group_id, re.expense_name, re.amount, re.billing_day, gl.group_name
        FROM recurring_expenses re
        JOIN group_list gl ON re.group_id = gl.group_id
        WHERE re.user_id = :uid
    """
    params = {"uid": user_id}
    
    # Only filter by group if a specific group (ID > 0) is selected
    if group_id and group_id != 0:
        query_str += " AND re.group_id = :gid"
        params["gid"] = group_id
        
    query = text(query_str)
    with engine.connect() as conn:
        result = conn.execute(query, params).fetchall()
        return [dict(row._asdict()) for row in result]

def update_recurring_expense(recurring_id, name, amount, day):
    """Updates an existing recurring expense including the billing day."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE recurring_expenses 
            SET expense_name = :name, amount = :amount, billing_day = :day 
            WHERE recurring_id = :rid
        """), {"name": name, "amount": amount, "day": day, "rid": recurring_id})

def delete_recurring_expense(recurring_id):
    """Permanently removes a recurring expense rule."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM recurring_expenses WHERE recurring_id = :rid"), 
                     {"rid": recurring_id})