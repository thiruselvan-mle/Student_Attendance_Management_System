from flask import Flask , Blueprint , redirect , url_for , render_template , request , flash , session
from datetime import date, datetime
import calendar

from models.incharge_model import incharge_table
from models.incharge_model import students_list
from models.incharge_model import load_cls_timetable
from models.incharge_model import attendance_list
from models.incharge_model import incharege_timetable
from models.incharge_model import current_month_list
from models.incharge_model import get_semester_date

from utils.incharge_utils import calculate_percentage
from utils.incharge_utils import incharge_shedule
from utils.incharge_utils import today_incharge_periods
from utils.incharge_utils import count_students
from utils.incharge_utils import load_incharge_timetable
from utils.incharge_utils import month_calculation
from utils.incharge_utils import students_monthly_report
from utils.incharge_utils import get_month_ranges

incharge = Blueprint('incharge', __name__, url_prefix='/incharge')

@incharge.route('/dashboard', methods=['GET'])
def incharge_dashboard():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))

    try:
        incharge_id = session['incharge_id'].strip().lower()

        # 🔹 Get all departments handled by incharge
        rows = incharge_table(incharge_id)

        if not rows:
            flash("No department assigned", "error")
            return redirect(url_for('auth.login'))

        departments = [r['department'].strip().lower() for r in rows]

        # 🔹 Set default department (FIRST TIME ONLY)
        if 'active_department' not in session or session['active_department'] not in departments:
            session['active_department'] = departments[0]

        active_department = session['active_department']

        # 🔹 Get active department row
        active_row = next(
            r for r in rows
            if r['department'].strip().lower() == active_department
        )

        if not active_row:
            session.pop('active_department', None)
            return redirect(url_for('incharge.incharge_dashboard'))
        
        semester = active_row['semester']
        year = active_row['year']

        # 🔹 Students
        students = students_list(semester, active_department)
        register_no = [s['register_no'] for s in students]
        gender = [s['gender'] for s in students]

        total_count, male_count, female_count = count_students(register_no, gender)
        attendance = attendance_list(register_no)
        overall_percentage = calculate_percentage(attendance)

        # 🔹 Today timetable
        today = date.today()
        day = today.strftime("%A")
        incharge_timetable = load_cls_timetable(semester, active_department, day)
        schedule = incharge_shedule(incharge_timetable)
        today_periods = today_incharge_periods(schedule)

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.login"))
    
    return render_template(
        'incharge/dashboard.html',
        incharge=active_row,          # ✅ only active department
        departments=departments,      # ✅ list for navbar
        active_department=active_department,
        male=male_count,
        female=female_count,
        total_students=total_count,
        overall_percentage=overall_percentage,
        today_periods=today_periods
    )

@incharge.route("/switch-department/<dept>")
def switch_department(dept):
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))

    try:
        session['active_department'] = dept.lower()
    
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("incharge.incharge_dashboard"))
    
    return redirect(url_for('incharge.incharge_dashboard'))

@incharge.route('/incharge/timetable', methods = ["GET","POST"])
def incharge_timetable():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        incharge_id = session['incharge_id'].strip().lower()

        # 🔹 Get all departments handled by incharge
        rows = incharge_table(incharge_id)
        department = session['active_department']
        active_row = next(
            r for r in rows
            if r['department'].strip().lower() == department
        )

        if not active_row:
            session.pop('active_department', None)
            return redirect(url_for('incharge.incharge_dashboard'))

        semester = active_row['semester']
        year = active_row['year']
        row = incharege_timetable(semester, department)
        timetable = load_incharge_timetable(row)

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("incharge.incharge_dashboard"))
    
    return render_template(
    'incharge/timetable.html',
    year = year,
    timetable =timetable,
    department = department
    )

@incharge.route("/monthly/report/")
def monthly_report():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        incharge_id = session['incharge_id'].strip().lower()

        # 🔹 Get all departments handled by incharge
        rows = incharge_table(incharge_id)
        department = session['active_department']
        active_row = next(
            r for r in rows
            if r['department'].strip().lower() == department
        )

        if not active_row:
            session.pop('active_department', None)
            return redirect(url_for('incharge.incharge_dashboard'))
        semester = active_row['semester']
        year = active_row['year']

        students = students_list(semester, department)
        row = [s['register_no'] for s in students]

        today = date.today()
        current_year = today.year

        selected_month = int(request.args.get('month', date.today().month))
        month_name = calendar.month_name[selected_month]

        month_start, month_end = month_calculation(selected_month, today, current_year)
        month_range = get_month_ranges(current_year)

        lst = current_month_list(month_start,month_end,row)
        reports, total_days = students_monthly_report(lst)
        
        sem_date = get_semester_date(semester, department, year)
        if sem_date:
            start_date = sem_date['start_date']
            end_date = sem_date['end_date'] 

        else:
            flash("Please Inform admin to update semester Duration Dates", "error")
            return redirect(url_for('incharge.incharge_dashboard'))
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("incharge.incharge_dashboard"))
    
    return render_template(
    "incharge/monthly_report.html",
    department = department,
    month = month_name,
    semester = semester,
    year = year,
    today = today,
    reports = reports,
    total_days = total_days,
    current_year = current_year,
    date = date,
    month_ranges = month_range,
    semester_start = start_date,
    semester_end = end_date,
    selected_month =selected_month
    )

@incharge.route("/incharge/profile/")
def incharge_profile():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:

        incharge_id = session['incharge_id'].strip().lower()

        # 🔹 Get all departments handled by incharge
        rows = incharge_table(incharge_id)
        department = session['active_department']
        active_row = next(
            r for r in rows
            if r['department'].strip().lower() == department
        )
        
        if not active_row:
            session.pop('active_department', None)
            return redirect(url_for('incharge.incharge_dashboard'))
        
        gender = active_row['gender'].strip().lower()

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("incharge.incharge_dashboard"))
    
    return render_template(
    'incharge/profile.html',
    gender = gender,
    department = department,
    incharge = active_row)
