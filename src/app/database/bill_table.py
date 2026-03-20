from sqlalchemy import text
from app.database.database import *
from src.app.database.group_table import *
from src.app.database.member_table import *
from src.app.database.profile_table import *
from src.app.database.bill_table import *
from src.app.database.payment_table import *

def save_bill_history(user_id, df):
    engine = get_engine()
    df_to_save = df.copy()
    df_to_save["user_id"] = user_id
    df_to_save.to_sql("bill_history", engine, if_exists="append", index=False)