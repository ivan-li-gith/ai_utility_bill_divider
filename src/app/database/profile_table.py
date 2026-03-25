from sqlalchemy import text
from .database import get_engine

def get_profile(user_id):
    engine = get_engine()
    query = text("SELECT * FROM profiles WHERE user_id = :uid")
    
    with engine.connect() as conn:
        result = conn.execute(query, {"uid": user_id}).fetchone()
        return result._asdict() if result else None
    
def save_profile(user_id, name, email, phone):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO profiles (user_id, display_name, email, phone)
            VALUES (:uid, :name, :email, :phone)
            ON DUPLICATE KEY UPDATE display_name = :name, email = :email, phone = :phone
        """), {"uid": user_id, "name": name, "email": email, "phone": phone})
        
def get_user_by_email(email):
    """Finds a user's ID by their email."""
    engine = get_engine()
    query = text("SELECT user_id FROM profiles WHERE email = :email")
    with engine.connect() as conn:
        result = conn.execute(query, {"email": email}).fetchone()
        return result[0] if result else None