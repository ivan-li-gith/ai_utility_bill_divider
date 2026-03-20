import pandas as pd
from sqlalchemy import text
from .database import get_engine

def save_bill_history(user_id, df):
    engine = get_engine()
    df_to_save = df.copy()
    df_to_save["user_id"] = user_id
    df_to_save.to_sql("bill_history", engine, if_exists="append", index=False)

def load_history(user_id, group_id=None):
    """Fetches bill history, explicitly filtered by group."""
    engine = get_engine()
    if group_id:
        query = text("SELECT * FROM bill_history WHERE user_id = :uid AND group_id = :gid")
        return pd.read_sql(query, engine, params={"uid": user_id, "gid": group_id})
    else:
        query = text("SELECT * FROM bill_history WHERE user_id = :uid")
        return pd.read_sql(query, engine, params={"uid": user_id})

def save_tracker(user_id, df, month, group_id):
    """Saves payment status for a specific group and month."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM payment_tracker 
            WHERE `Billing Month` = :month AND user_id = :uid AND group_id = :gid
        """), {"month": month, "uid": user_id, "gid": group_id})
    
    df_to_save = df.copy()
    df_to_save["Billing Month"] = month
    df_to_save["user_id"] = user_id
    df_to_save["group_id"] = group_id
    
    cols = ["user_id", "group_id", "Billing Month", "Roommate Name", "Current Month Split", "Rollover Amount", "Total Owed", "Paid"]
    df_to_save[cols].to_sql("payment_tracker", engine, if_exists="append", index=False)
    
def get_paid_status(user_id, month, group_id):
    """Fetches paid status for a specific group and month."""
    engine = get_engine()
    query = text("""
        SELECT `Roommate Name`, `Paid` 
        FROM payment_tracker 
        WHERE `Billing Month` = :month AND user_id = :uid AND group_id = :gid
    """)
    
    try:
        df = pd.read_sql(query, engine, params={"month": month, "uid": user_id, "gid": group_id})
        if not df.empty:
            return df.set_index("Roommate Name")["Paid"].to_dict()
        return {}
    except Exception:
        return {}