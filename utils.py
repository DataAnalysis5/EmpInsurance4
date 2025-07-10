from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId
from bson import ObjectId, errors as bson_errors
from extensions import employees_collection

def calc_age(dob_str):
    try:
        dob = date.fromisoformat(dob_str)
        today = date.today()

        delta = relativedelta(today, dob)

        if delta.years == 0:
            if delta.months == 0:
                if delta.days <= 1:
                    return "Newborn"
                return f"{delta.days} days"
            elif delta.days > 15:
                return f"{delta.months + 1} months"
            return f"{delta.months} months"
        elif delta.years == 1 and delta.months == 0 and delta.days == 0:
            return "1 year"
        else:
            return f"{delta.years} years"
    except Exception:
        return ""


def normalize_family(emp):
    emp['spouse'] = {'name': '', 'date_of_birth': '', 'phone': '', 'gender': '', 'age': ''}
    emp['children'] = []
    emp['parents'] = []
    family = emp.get('family_members', [])
    for member in family:
        rel = member.get('relationship', '')
        name = member.get('name', '')
        dob = member.get('date_of_birth', '')
        gender = member.get('gender', '')
        age = member.get('age', '') or (calc_age(dob) if dob else '')
        if rel == 'Spouse':
            emp['spouse'] = {
                'name': name,
                'date_of_birth': dob,
                'phone': member.get('phone', ''),
                'gender': gender,
                'age': age
            }
        elif rel == 'Child':
            emp['children'].append({
                'name': name,
                'date_of_birth': dob,
                'phone': member.get('phone', ''),
                'gender': gender,
                'age': age
            })
        elif rel in ['Mother', 'Father']:
            emp['parents'].append({
                'relationship': rel,
                'name': name,
                'date_of_birth': dob,
                'age': age
            })
    for m in family:
        if not m.get('age') and m.get('date_of_birth'):
            m['age'] = calc_age(m['date_of_birth'])
    emp['family_members'] = family
    return emp

def format_date_ddmmyyyy(date_str):
    if not date_str:
        return ''
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y', '%Y.%m.%d', '%d.%m.%Y'):
        try:
            d = datetime.strptime(date_str, fmt)
            return d.strftime('%d-%m-%Y')
        except Exception:
            continue
    return date_str  # fallback

def _get_employee_by_session_id(emp_id):
    """
    Fetches employee by _id or employee_id string.
    Returns None if nothing found or invalid ID format.
    """
    if not emp_id:
        return None

    try:
        return employees_collection.find_one({'_id': ObjectId(emp_id)})
    except (bson_errors.InvalidId, TypeError):
        return employees_collection.find_one({'employee_id': emp_id})
