import json
from src.app.database import get_user_groups, create_group, add_group_member, get_group_members, update_group_name, update_and_sync_member, delete_member

# grabs member data and converts from json strings to list
def fetch_user_groups(user_id):
    user_groups = get_user_groups(user_id)
    for group in user_groups:
        members_data = group.get('members_json')
        if isinstance(members_data, str):
            try:
                group['members'] = json.loads(members_data)
            except json.JSONDecodeError:
                group['members'] = []
        else:
            group['members'] = members_data or []
    return user_groups

def add_new_group(user_id, group_name, group_type, names, emails):
    if group_type == 'individual' and names:
        group_name = names[0]
        
    if not group_name:
        raise ValueError("Group name is required.")
        
    group_id = create_group(user_id, group_name, group_type)
    process_members(user_id, group_id, names, emails, auto_create_individual=(group_type == 'group'))
    return group_name

def modify_group(user_id, group_id, group_type, new_name, existing_data, new_data):
    if group_type == 'individual':
        names, emails = existing_data['names'], existing_data['emails']
        if names:
            clean_name = names[0].strip()
            clean_email = emails[0].strip() if emails else ""
            
            if clean_name:
                members = get_group_members(group_id)
                target = next((m for m in members if m['role'] != 'owner'), None)
                if target:
                    update_and_sync_member(target['group_member_id'], user_id, clean_name, clean_email)  
    else:
        if new_name:
            update_group_name(group_id, new_name)
            
        current_members = get_group_members(group_id)
        submitted_ids = [str(i) for i in existing_data['ids']]
        
        for member in current_members:
            m_id_str = str(member['group_member_id'])
            # If a member is not the owner and is missing from the submitted list, delete them
            if member['role'] != 'owner' and m_id_str not in submitted_ids:
                delete_member(member['group_member_id'])
                
        for m_id, name, email in zip(existing_data['ids'], existing_data['names'], existing_data['emails']):
            clean_name = name.strip()
            if clean_name:
                update_and_sync_member(m_id, user_id, clean_name, email.strip())
                
        process_members(user_id, group_id, new_data['names'], new_data['emails'], auto_create_individual=True)

# adds members to group and creates individual cards for them
def process_members(user_id, group_id, names, emails, auto_create_individual=False):
    for name, email in zip(names, emails): 
        clean_name = name.strip()
        clean_email = email.strip() if email else ""
        
        if clean_name:
            add_group_member(group_id, clean_name, clean_email) 
            if auto_create_individual:
                ensure_individual_exists(user_id, clean_name, clean_email)

# prevents duplicate members
def ensure_individual_exists(owner_id, name, email):
    clean_name = name.strip()
    clean_email = email.strip() if email else ""
    existing_groups = get_user_groups(owner_id)
    
    for group in existing_groups:
        if group.get('group_type') == 'individual':
            members = group.get('members_json', [])
            if isinstance(members, str):
                members = json.loads(members)
            
            for m in members:
                if m.get('role') == 'owner': 
                    continue
                if (clean_email and m.get('email') == clean_email) or (not clean_email and m.get('name') == clean_name):
                    return 

    new_id = create_group(owner_id, clean_name, 'individual')
    add_group_member(new_id, clean_name, clean_email)