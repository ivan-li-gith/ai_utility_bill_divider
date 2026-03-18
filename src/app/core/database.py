import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS") 
DB_NAME = os.environ.get("DB_NAME")

def get_engine():
    connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"
    return create_engine(connection_string)

def init_db():
    engine = get_engine()
    with engine.begin() as conn:
        # bill_history table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bill_history (
                user_id VARCHAR(255),
                `Billing Month` VARCHAR(255),
                `Service Name` VARCHAR(255),
                `Service Period` VARCHAR(255),
                `Total Amount Due` DECIMAL(10, 2)
            )
        """))
        
        # payment_tracker table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS payment_tracker (
                user_id VARCHAR(255),
                `Billing Month` VARCHAR(255),
                `Roommate Name` VARCHAR(255),
                `Current Month Split` DECIMAL(10, 2),
                `Rollover Amount` DECIMAL(10, 2),
                `Total Owed` DECIMAL(10, 2),
                `Paid` BOOLEAN
            )
        """))
        
        # roommates table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS roommates (
                user_id VARCHAR(255),
                `Roommate Name` VARCHAR(255),
                UNIQUE(user_id, `Roommate Name`)
            )
        """))

def load_history(user_id):
    engine = get_engine()
    query = text("SELECT * FROM bill_history WHERE user_id = :uid")
    return pd.read_sql(query, engine, params={"uid": user_id})

def clear_db(user_id):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM bill_history WHERE user_id = :uid"), {"uid": user_id})
        conn.execute(text("DELETE FROM payment_tracker WHERE user_id = :uid"), {"uid": user_id})

def save_tracker(user_id, df, month):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM payment_tracker 
            WHERE `Billing Month` = :month AND user_id = :uid
        """), {"month": month, "uid": user_id})
    
    df_to_save = df.copy()
    df_to_save["Billing Month"] = month
    df_to_save["user_id"] = user_id
    
    cols = ["user_id", "Billing Month", "Roommate Name", "Current Month Split", "Rollover Amount", "Total Owed", "Paid"]
    df_to_save[cols].to_sql("payment_tracker", engine, if_exists="append", index=False)

def get_roommates(user_id):
    engine = get_engine()
    query = text("SELECT `Roommate Name` FROM roommates WHERE user_id = :uid")
    
    try:
        df = pd.read_sql(query, engine, params={"uid": user_id})
        return df["Roommate Name"].tolist()
    except Exception:
        return []

def add_roommate(user_id, name):
    engine = get_engine()
    name = name.strip()
    if not name:
        return
    with engine.begin() as conn:
        try:
            conn.execute(text("""
                INSERT INTO roommates (user_id, `Roommate Name`)
                VALUES (:uid, :name)
            """), {"uid": user_id, "name": name})
        except Exception: 
            pass

def remove_roommate(user_id, name):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM roommates 
            WHERE user_id = :uid AND `Roommate Name` = :name
        """), {"uid": user_id, "name": name})

def save_bill_history(user_id, df):
    engine = get_engine()
    df_to_save = df.copy()
    df_to_save["user_id"] = user_id
    df_to_save.to_sql("bill_history", engine, if_exists="append", index=False)

def get_paid_status(user_id, month):
    engine = get_engine()
    query = text("""
        SELECT `Roommate Name`, `Paid` 
        FROM payment_tracker 
        WHERE `Billing Month` = :month AND user_id = :uid
    """)
    
    try:
        df = pd.read_sql(query, engine, params={"month": month, "uid": user_id})
        if not df.empty:
            return df.set_index("Roommate Name")["Paid"].to_dict()
        return {}
    except Exception:
        return {}