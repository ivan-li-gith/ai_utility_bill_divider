from src.app.database.db import db_session
from src.app.database.models import Profile

def get_profile(user_id):
    profile = db_session.query(Profile).filter_by(user_id=user_id).first()
    if profile:
        return {"user_id": profile.user_id, "display_name": profile.display_name, "email": profile.email, "phone": profile.phone}
    return None
    
def save_profile(user_id, name, email, phone):
    profile = db_session.query(Profile).filter_by(user_id=user_id).first()
    if profile:
        profile.display_name = name
        profile.email = email
        profile.phone = phone
    else:
        profile = Profile(user_id=user_id, display_name=name, email=email, phone=phone)
        db_session.add(profile)
    db_session.commit()
        
def get_user_by_email(email):
    profile = db_session.query(Profile).filter_by(email=email).first()
    return profile.user_id if profile else None