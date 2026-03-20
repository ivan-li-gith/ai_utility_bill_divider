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

def clear_db(user_id):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM bill_history WHERE user_id = :uid"), {"uid": user_id})
        conn.execute(text("DELETE FROM payment_tracker WHERE user_id = :uid"), {"uid": user_id})