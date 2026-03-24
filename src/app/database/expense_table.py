# src/app/database/expense_table.py
from sqlalchemy import text
from .database import get_engine

def save_new_expense(group_id, user_id, date, item_name, amount, payer_id, split_method):
    """Saves a one-off expense AND automatically generates the debt splits for the group."""
    engine = get_engine()
    
    with engine.begin() as conn:
        # 1. Save the main expense record
        result = conn.execute(text("""
            INSERT INTO receipt_expenses 
            (group_id, user_id, expense_date, description, amount, payer_id, split_method)
            VALUES (:gid, :uid, :date, :desc, :amt, :payer, :split)
        """), {
            "gid": group_id, "uid": user_id, "date": date, 
            "desc": item_name, "amt": amount, "payer": payer_id, "split": split_method
        })
        
        expense_id = result.lastrowid
        
        # 2. Fetch the group members to calculate the split
        members_query = text("SELECT member_name, user_id FROM group_members WHERE group_id = :gid")
        members = conn.execute(members_query, {"gid": group_id}).fetchall()
        
        if not members:
            return
            
        # 3. Calculate the even split
        num_people = len(members)
        split_amount = round(amount / num_people, 2)
        
        # 4. Assign the debt to everyone except the person who paid
        for member in members:
            # Check if this member is the payer (by matching user_id)
            is_payer = str(member.user_id) == str(payer_id)
            
            if not is_payer:
                conn.execute(text("""
                    INSERT INTO expense_splits (expense_id, roommate_name, amount_owed, is_paid)
                    VALUES (:eid, :name, :owed, FALSE)
                """), {
                    "eid": expense_id,
                    "name": member.member_name,
                    "owed": split_amount
                })

def load_expense_history(group_id):
    """Fetches all receipt/manual expenses for a specific group to display in the table."""
    engine = get_engine()
    query = text("""
        SELECT e.expense_id, e.expense_date, e.description, e.amount, e.payer_id, e.split_method, g.group_name 
        FROM receipt_expenses e
        JOIN group_list g ON e.group_id = g.group_id
        WHERE e.group_id = :gid
        ORDER BY e.expense_date DESC
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"gid": group_id}).fetchall()
        return [dict(row._asdict()) for row in result]
        
def delete_expense(expense_id):
    """Removes a specific expense from the ledger."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM receipt_expenses WHERE expense_id = :eid"), {"eid": expense_id})
        
def get_unpaid_expense_splits(group_id=None):
    """Fetches all unpaid one-off expenses owed to the user."""
    engine = get_engine()
    
    query_str = """
        SELECT es.roommate_name, SUM(es.amount_owed) as total_owed
        FROM expense_splits es
        JOIN receipt_expenses re ON es.expense_id = re.expense_id
        WHERE es.is_paid = FALSE
    """
    params = {}
    
    # Filter by a specific group if requested from the dashboard dropdown
    if group_id and group_id != 0:
        query_str += " AND re.group_id = :gid"
        params["gid"] = group_id
        
    query_str += " GROUP BY es.roommate_name"
    
    with engine.connect() as conn:
        result = conn.execute(text(query_str), params).fetchall()
        return {row.roommate_name: float(row.total_owed) for row in result}