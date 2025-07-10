from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId  
from models import employees_collection
from forms import CSRFOnlyForm

auth_bp = Blueprint('auth', __name__)

# ── Helper to fetch an employee safely ───────────────────────────
def _get_employee_by_session_id(emp_id):
    """
    Return the employee document or None.

    Handles:
      - Missing / empty IDs
      - Badly‑formed ObjectIds
      - Numeric employee_id fallback
    """
    if not emp_id:
        return None

    try:
        return employees_collection.find_one({'_id': ObjectId(emp_id)})
    except Exception:
        return employees_collection.find_one({'employee_id': emp_id})


@auth_bp.route('/')
def landing():
    return render_template('landing.html')


@auth_bp.route('/dashboard')
def dashboard():
    role = session.get('role')

    # ── 1. Admins ──────────────────────────
    if role == 'admin':
        return redirect(url_for('auth.dashboard'))
        #return redirect(url_for('admin.admin_dashboard'))

    # ── 2. Logged‑in normal user ───────────
    if role == 'user':
        emp_id = session.get('employee_id') or session.get('mongo_id')
        employee = _get_employee_by_session_id(emp_id)

        if employee is None:
            session.clear()
            flash('Your session has expired. Please log in again.', 'info')
            return redirect(url_for('auth.dashboard', show_login=1))

        if not employee.get('details_completed'):
            return redirect(url_for('main.complete_profile'))

        return redirect(url_for('main.employee_detail'))

    # ── 3. Not logged in (show Register/Login tabs) ──
    form = CSRFOnlyForm()
    return render_template('dashboard.html', form=form)


@auth_bp.route('/register', methods=['POST'])
def register():
    form = CSRFOnlyForm()
    if not form.validate_on_submit():
        flash('Invalid or missing CSRF token.', 'danger')
        return render_template('dashboard.html', form=form)

    name = request.form.get('name')
    phone = request.form.get('phone')
    password = request.form.get('password')

    if not all([name, phone, password]):
        flash('All fields are required.', 'danger')
        return render_template('dashboard.html', form=form)

    if employees_collection.find_one({'phone': phone}):
        flash('An account with this phone already exists.', 'danger')
        return render_template('dashboard.html', form=form)

    hashed_pw = generate_password_hash(password)
    result = employees_collection.insert_one({
        'name': name,
        'phone': phone,
        'password': hashed_pw,
        'details_completed': False
    })

    session['mongo_id'] = str(result.inserted_id)
    session['role'] = 'user'
    flash('Registration successful.', 'success')
    return redirect(url_for('main.complete_profile'))

@auth_bp.route('/login', methods=['POST'])
def login():
    form = CSRFOnlyForm()
    if not form.validate_on_submit():
        flash('Invalid or missing CSRF token.', 'danger')
        return render_template('dashboard.html', form=form, show_login=1)

    identifier = request.form.get('identifier')
    password = request.form.get('passcode')
    role = request.form.get('role')

    if role == 'admin':
        admin = employees_collection.find_one({'role': 'admin'})
        if admin and check_password_hash(admin['password'], password):
            session['role'] = 'admin'
            flash('Admin login successful.', 'success')
            #return redirect(url_for('auth.dashboard'))
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('auth.dashboard', show_login=1))


    elif role == 'user':
        if not identifier or not identifier.isdigit() or len(identifier) != 10:
            flash('Mobile number must be exactly 10 digits.', 'danger')
            return redirect(url_for('auth.dashboard', show_login=1))

        employee = employees_collection.find_one({'phone': identifier})
        if employee and check_password_hash(employee.get('password', ''), password):
            session['role'] = 'user'
            session['mongo_id'] = str(employee['_id'])
            session['employee_id'] = employee.get('employee_id', '')
            session['user_phone'] = employee['phone']
            # Preserve the 'details_completed' flag from the database
            #session['details_completed'] = employee.get('details_completed', False)
            
            if not employee.get('details_completed'):
                return redirect(url_for('main.complete_profile'))
            flash('Login successful.', 'success')
            return redirect(url_for('main.employee_detail'))
        else:
            flash('Invalid user credentials.', 'danger')
            return redirect(url_for('auth.dashboard', show_login=1))

    else:
        flash('Invalid role selected.', 'danger')
        return redirect(url_for('auth.dashboard', show_login=1))

@auth_bp.route('/logout')
def logout():
    # Clearing only sensitive session data related to login 
    session.pop('role', None)
    session.pop('mongo_id', None)
    session.pop('employee_id', None)
    session.pop('user_phone', None)
    #session.pop('details_completed', None) 

    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.dashboard'))