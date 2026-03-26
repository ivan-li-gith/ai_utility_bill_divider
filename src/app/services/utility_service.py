import pandas as pd
from src.app.core.parser import extract_from_pdf, get_bill_details
from src.app.database import get_group_members, save_utility_bills, get_utility_bills, save_utility_splits, get_utility_split_status

# extracts info from pdfs
def process_uploaded_bills(files):
    all_bill_data = []
    errors = []
    
    for file in files:
        if file.filename.endswith('.pdf'):
            try:
                extracted_text = extract_from_pdf(file)
                bill_data = get_bill_details(extracted_text)
                all_bill_data.append(bill_data)
            except Exception as e:
                errors.append(f"Failed to process {file.filename}: {e}")
                
    return all_bill_data, errors

# the review part of the pdf scan before saving
def format_and_save_bills(user_id, group_id, bill_count, form_data):
    corrected_data = []
    
    for i in range(bill_count):
        month = form_data.get(f"month_{i}")
        if month in ["Unknown", "Error", ""]:
            raise ValueError(f"Row {i+1} has an invalid month. Please correct it before saving.")
        
        corrected_data.append({
            "Billing Month": form_data.get(f"month_{i}"),
            "Service Name": form_data.get(f"service_{i}"),
            "Service Period": form_data.get(f"period_{i}"),
            "Total Amount Due": float(form_data.get(f"amount_{i}", 0)),
            "group_id": group_id
        })

    if corrected_data:
        df = pd.DataFrame(corrected_data)
        save_utility_bills(user_id, df)
        return True
    return False

# adds me to the list of roommate names
def get_member_names(user_id, members):
    return ["Me" if str(m.get("user_id")) == str(user_id) else m["member_name"] for m in members]

# recalculates all the balances when user marks something as paid
def process_status_update(user_id, group_id, month, form_data):
    members = get_group_members(group_id)
    names = get_member_names(user_id, members)
    
    updated_rows = []    
    for name in names:
        is_paid = form_data.get(f"paid_{month}_{name}") == 'on'
        split_val = float(form_data.get(f"split_{month}_{name}", 0))
        rollover_val = float(form_data.get(f"rollover_{month}_{name}", 0))
        total_val = round(split_val + rollover_val, 2)

        updated_rows.append({
            "Roommate Name": name,
            "Paid": is_paid,
            "Current Month Split": split_val,
            "Rollover Amount": rollover_val,
            "Total Owed": total_val
        })
        
    df = pd.DataFrame(updated_rows)
    save_utility_splits(user_id, df, month, group_id)
    
    billing_history = get_utility_bills(user_id, group_id)
    updated_months = calculate_utilities(user_id, billing_history, names, group_id)
    
    all_updates = {}
    for m in updated_months:
        month_name = m['month']
        all_updates[month_name] = {
            row['Roommate Name']: {
                "total": f"{row['Total Owed']:.2f}",
                "rollover": f"{row['Rollover Amount']:.2f}"
            }
            for _, row in m['roommates'].iterrows()
        }
    return all_updates

# calculates monthly utility splits
def calculate_utilities(user_id, billing_history, names, group_id):
    unique_months = billing_history["Billing Month"].unique()
    months_ascending = sorted(unique_months, key=lambda d: pd.to_datetime(d, format='%B %Y'))
    running_rollover = {name: 0.0 for name in names}
    month_displays = []

    for month in months_ascending:
        month_df = billing_history[billing_history["Billing Month"] == month]
        monthly_total = month_df["Total Amount Due"].sum()
        num_ppl = len(names)
        monthly_split = round(monthly_total / num_ppl, 2) if num_ppl > 0 else 0
        paid_dict = get_utility_split_status(user_id, month, group_id)
        
        roommates = pd.DataFrame({
            "Roommate Name": names,
            "Current Month Split": monthly_split,
            "Rollover Amount": [running_rollover[name] for name in names],
            "Paid": [bool(paid_dict.get(name, False)) for name in names]
        })
        
        roommates["Total Owed"] = (roommates["Current Month Split"] + roommates["Rollover Amount"]).round(2)
        
        for _, row in roommates.iterrows():
            running_rollover[row["Roommate Name"]] = 0.0 if row["Paid"] else row["Total Owed"]
        
        month_displays.append({
            "month": month,
            "df": month_df,
            "roommates": roommates,
            "monthly_total": monthly_total,
            "monthly_split": monthly_split,
            "group_id": group_id
        })
        
    return month_displays