from sqlalchemy import text
from .database import get_engine

def add_subscription(user_id, group_id, name, amount, day):
    """Adds a new fixed subscription expense rule including the billing day."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO subscription_expenses (user_id, group_id, expense_name, amount, billing_day)
            VALUES (:uid, :gid, :name, :amount, :day)
        """), {"uid": user_id, "gid": group_id, "name": name, "amount": amount, "day": day})

def get_subscription(user_id, group_id=None):
    """Fetches subscription expenses. If group_id is 0 or None, fetches all for the user."""
    engine = get_engine()
    
    # JOIN with group_list to get the group_name for the "Charging: X" label
    query_str = """
        SELECT re.subscription_id, re.group_id, re.expense_name, re.amount, re.billing_day, gl.group_name
        FROM subscription_expenses re
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

def update_subscription(subscription_id, name, amount, day):
    """Updates an existing subscription expense including the billing day."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE subscription_expenses 
            SET expense_name = :name, amount = :amount, billing_day = :day 
            WHERE subscription_id = :rid
        """), {"name": name, "amount": amount, "day": day, "rid": subscription_id})

def delete_subscription(subscription_id):
    """Permanently removes a subscription expense rule."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM subscription_expenses WHERE subscription_id = :rid"), 
                     {"rid": subscription_id})