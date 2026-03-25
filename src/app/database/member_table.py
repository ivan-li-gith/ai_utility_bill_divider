from sqlalchemy import text
from .database import get_engine

def add_group_member(group_id, name, email, phone=""):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO group_members (group_id, member_name, member_email, member_phone)
            VALUES (:gid, :name, :email, :phone)
        """), {"gid": group_id, "name": name, "email": email, "phone": phone})
        
def delete_member(member_id):
    """Deletes a specific member from a group."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM group_members WHERE group_member_id = :mid AND role != 'owner'"), 
                     {"mid": member_id})
        
def update_member(member_id, name, email, phone=""):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE group_members 
            SET member_name = :name, member_email = :email, member_phone = :phone 
            WHERE group_member_id = :mid AND role != 'owner'
        """), {"name": name, "email": email, "phone": phone, "mid": member_id})
        
def get_group_members(group_id):
    """Fetches all members in a group directly from the members table."""
    engine = get_engine()
    # Remove the JOIN with profiles so unregistered members are included
    query = text("""
        SELECT member_name, member_email, member_phone, user_id, role
        FROM group_members
        WHERE group_id = :gid
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"gid": group_id}).fetchall()
        return [dict(row._asdict()) for row in result]

def get_group_member_names(group_id):
    """Returns a simple list of names for members in a group."""
    engine = get_engine()
    query = text("SELECT member_name FROM group_members WHERE group_id = :gid")
    with engine.connect() as conn:
        result = conn.execute(query, {"gid": group_id}).fetchall()
        return [row[0] for row in result]