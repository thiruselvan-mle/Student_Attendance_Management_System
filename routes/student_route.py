from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from datetime import datetime, date, timedelta

from models.student_model import dashboard_student
from models.student_model import dashboard_attendance
from models.student_model import dashboard_today_status
from models.student_model import dashboard_total_days
from models.student_model import get_timetable
from models.student_model import get_active_semester
from models.student_model import student_day_attendance

from utils.student_utils import percentage_calculation
from utils.student_utils import current_status
from utils.student_utils import load_timetable
from utils.student_utils import build_week_attendance
from utils.student_utils import get_subject_total_periods
from utils.student_utils import get_subject_present_count
from utils.student_utils import get_subject_overview
from utils.student_utils import batch_calculation

student = Blueprint('student', __name__, url_prefix='/student')

@student.route('/dashboard', methods = ['GET', 'POST'])
def student_dashboard():
    if 'register_no' not in session:
        return redirect(url_for('auth.login'))
    
    register_no = session['register_no']
    result_student = dashboard_student(register_no)

    if not result_student:
        return 'Student Not Found!'
    
    name = result_student['name']
    department = result_student['department'] 
    year = result_student['year']
    class_name = result_student['class_name'] 
    semester = result_student['semester']

    result_attendance = dashboard_attendance(register_no)
    present_percent, absent_percent = percentage_calculation(result_attendance)
    
    today = date.today().isoformat()
    result_today_status = dashboard_today_status(register_no,today )
    today_status = current_status(result_today_status)
    result_total_days =  dashboard_total_days(register_no)
    
    return render_template('student/dashboard.html',
        student_name=name,
        department=department,
        year=year,
        class_name=class_name,
        present_percent=present_percent,
        absent_percent=absent_percent,
        total_days=result_total_days,
        today_status=today_status
    )

@student.route('/get_week_attendance')
def get_week_attendance_api():
    if 'register_no' not in session:
        return jsonify({})

    register_no = session['register_no']
    result_student = dashboard_student(register_no)

    department = result_student['department']
    year = result_student['year']
    class_name = result_student['class_name']
    semester = result_student['semester']

    result_timetable = get_timetable(department, year, class_name, semester)
    timetable = load_timetable(result_timetable)

    base_date = datetime.strptime(request.args.get('date'), "%Y-%m-%d")
    response = build_week_attendance(base_date, register_no, timetable, student_day_attendance)
    
    return jsonify(response)

@student.route('/attendance_overview')
def student_attendance_overview():
    if 'register_no' not in session:
        return redirect(url_for('auth.login'))

    register_no = session['register_no']
    result_student =dashboard_student(register_no)

    department = result_student['department']
    year = result_student['year']

    result_active_status = get_active_semester(department , year)
    if not result_active_status:
        return render_template("student/no_active_semester.html")
    
    sem_start = result_active_status['start_date']
    sem_end = result_active_status['end_date']

    today = datetime.today().date()
    base_date = max(today, sem_start)
    monday = base_date - timedelta(days=base_date.weekday())

    return render_template(
        'student/attendance_overview.html',
        monday=monday.strftime("%Y-%m-%d"),
        week_start=monday.strftime("%d/%m/%Y"),
        week_end=(monday + timedelta(days=4)).strftime("%d/%m/%Y"),
        sem_start=sem_start.strftime("%Y-%m-%d"),
        sem_end=sem_end.strftime("%Y-%m-%d")
    )

@student.route("/subject_overview")
def student_subject_overview():
    if 'register_no' not in session:
        return redirect(url_for('auth.login'))

    register_no = session['register_no']
    result_student = dashboard_student(register_no)

    department = result_student['department']
    semester = result_student['semester']
    class_name = result_student['class_name']
    year = result_student['year']

    overview = get_subject_overview(register_no, department, semester, class_name , year, get_timetable, load_timetable, dashboard_attendance, get_subject_total_periods, get_subject_present_count)
    
    return render_template(
        "student/subject_overview.html",
        overview=overview
    )

@student.route("/profile")
def student_profile():
    if 'register_no' not in session:
        return redirect(url_for('auth.login'))

    register_no = session['register_no']
    result_student = dashboard_student(register_no)

    adm_year = result_student['admission_year']
    batch = batch_calculation(adm_year)

    return render_template(
        "student/student_profile.html",
        batch = batch,
        student=result_student
    )

