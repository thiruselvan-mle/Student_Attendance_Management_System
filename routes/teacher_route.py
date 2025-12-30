from flask import Flask , Blueprint , redirect , url_for , render_template , request , flash , session
from datetime import datetime , date

from models.teacher_model import teacher_table
from models.teacher_model import teacher_class
from models.teacher_model import get_student_list
from models.teacher_model import insrt_attendance_tabel
from models.teacher_model import insrt_lock
from models.teacher_model import is_attendance_locked
from models.teacher_model import teacher_marked_count
from models.teacher_model import get_teacher_timetable
from models.teacher_model import get_report
from models.teacher_model import take_attendance_report
from models.incharge_model import update_attendance
from models.incharge_model import update_attendance_lock

from utils.teacher_utils import teacher_shedule
from utils.teacher_utils import periods_calculation
from utils.teacher_utils import teacher_pending_count
from utils.teacher_utils import load_teacher_timetable
from utils.teacher_utils import build_attendance_report

teacher = Blueprint('teacher',__name__, url_prefix='/teacher')

@teacher.route('/dashboard')
def teacher_dashboard():
    if 'teacher_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['teacher_id']

    teacher = teacher_table(user_id)
    name = teacher['name']
    department = teacher['department']

    today = date.today()
    day = today.strftime("%A")

    teacher_timetable = teacher_class(user_id, day)
    result = teacher_shedule(teacher_timetable)
    today_periods, today_class_count = periods_calculation(result)
    marked_classes = teacher_marked_count(user_id, today)
    pending_classes=teacher_pending_count(today_class_count, marked_classes)
    
    return render_template(
        'teacher/dashboard.html',
        teacher_name=name,
        department=department,
        today_date=today,
        today=day,
        today_class=today_class_count,
        today_periods=today_periods,
        marked_classes=marked_classes,
        pending_classes=pending_classes
    )

@teacher.route('/attendance/mark/', methods =['POST','GET'])
def attendance_mark():
    if not any(role in session for role in ['teacher_id', 'incharge_id', 'hod_id']):
        return redirect(url_for('auth.login'))

    subject_name = None
    period = None
    today = date.today()
    class_name = None
    year = None
    department = None
    semester = None
    teacher_id = None

    if "teacher_id" in session:
        back_url = url_for('teacher.teacher_dashboard')
        mark_btn = True
        edit_btn = False

    elif "incharge_id" in session:
        back_url = url_for('incharge.incharge_dashboard')
        mark_btn = True
        edit_btn = True

    elif "hod_id" in session:
        back_url = url_for('hod.hod_dashboard')
        mark_btn = False
        edit_btn = True

    else:
        back_url = url_for('auth.login')

    if request.method == 'POST':        
        class_name = request.form['class_name']
        year = request.form['year']
        subject_name = request.form['subject_name']
        department = request.form['department']
        period = request.form['period_no']
        semester = request.form['semester']
        subject_code = request.form['subject_code']
        teacher_id = request.form['teacher_id']
        class_list = get_student_list(class_name, year, department, semester)

    return render_template(
        'teacher/attendance_mark.html',
        subject_name=subject_name,
        period=period,
        today_date=today,
        class_list = class_list,
        subject_code = subject_code,
        teacher_id = teacher_id,
        semester = semester,
        department = department,
        year = year,
        class_name =class_name,
        back_url = back_url,
        mark_btn = mark_btn,
        edit_btn = edit_btn
    )

@teacher.route('/attendance/submit/', methods =['POST','GET'])
def attendance_submit():
    if not any(role in session for role in ['teacher_id', 'incharge_id', 'hod_id']):
        return redirect(url_for('auth.login'))

    
    if request.method == 'POST':
        subject_code = request.form['subject_code']
        subject_name = request.form['subject_name']
        attendance_date = request.form['attendance_date']
        raw_period = request.form['period_no']
        period_no = int(raw_period.split(":")[1])
        semester = request.form['semester']
        teacher_id = request.form.get('teacher_id')
        department = request.form['department']
        class_name =request.form['class_name']
        submt_role = session['role']
        role = submt_role.lower()
        back_url = request.form.get('back_url')
        action = request.form.get('action')
        if not action:
            flash("Invalid request", "error")
            return redirect(back_url)
        
        if role == 'teacher':
            marked_by = session['teacher_id']

        elif role == 'incharge':
            marked_by = session['incharge_id']

        elif role == "hod":
            marked_by == session['hod_id']
        else:
            return redirect(url_for('auth.login'))

        if action == 'submit':
            if is_attendance_locked(attendance_date, period_no, department, semester, class_name, subject_code, teacher_id):
                flash("Attendance already submitted for this period!", "error")
                return redirect(back_url)
            
            for key, value in request.form.items():
                if key.startswith("status_"):
                    register_no = key.replace("status_", "")
                    status = value
                    name = request.form.get(f"name_{register_no}")
                    insrt_attendance_tabel(register_no, name, subject_name, subject_code, teacher_id, attendance_date, period_no, status, marked_by)          

            insrt_lock(attendance_date, period_no, department, semester, class_name, subject_code, marked_by, role, teacher_id)
            flash("Attendance submitted successfully!", "success")

            return redirect(back_url)
            
        elif action == 'edit':
            if not is_attendance_locked(attendance_date, period_no, department, semester, class_name, subject_code, teacher_id):
                flash("Attendance Not Yet Submitted!", "error")
                return redirect(back_url)
                
            for key, value in request.form.items():
                if key.startswith("status_"):
                    register_no = key.replace("status_", "")
                    status = value
                    name = request.form.get(f"name_{register_no}")
                    update_attendance(register_no, name, subject_name, subject_code, teacher_id, attendance_date, period_no, status, marked_by)
                
            update_attendance_lock(attendance_date, period_no, department, semester, class_name, subject_code, marked_by, role, teacher_id)
            flash("Attendance Updated Successfully!", "success")
            return redirect(back_url)

@teacher.route('/teacher/timetable/')
def timetable():
    if 'teacher_id' not in session:
        return redirect(url_for('auth.login'))
    
    teacher_id = session['teacher_id']
    teacher = teacher_table(teacher_id)
    department = teacher['department']
    load_timetable = get_teacher_timetable(teacher_id)
    timetable = load_teacher_timetable(load_timetable)
    
    return render_template('teacher/timetable.html' ,
    department = department, 
    timetable = timetable)

@teacher.route('/attendance/report/', methods = ["GET", "POST"])
def attendance_report():
    if 'teacher_id' not in session:
        return redirect(url_for('auth.login'))
    
    teacher_id = session['teacher_id']
    get_classes = get_teacher_timetable(teacher_id)
    classes = list(set(row['class_name'] for row in get_classes))

    department = None
    year = None
    reports = {}

    if request.method == "POST":
        semester =request.form['semester']
        class_name =request.form['class_name']

        students = get_report(semester, class_name)
        if students:
            register_no = [r['register_no'] for r in students]
            department = list(set(r['department'] for r in students))
            department = department[0] if department else None
            year = list(set(r['year'] for r in students))
            year = year[0] if year else None
            attendance_list = take_attendance_report(register_no)
            reports = build_attendance_report(attendance_list)

    return render_template(
    'teacher/attendance_report.html',
    classes = classes,
    department = department,
    year = year,
    reports = reports)

@teacher.route("/teacher/profile/")
def teacher_profile():
    if "teacher_id" not in session:
        return redirect(url_for('auth.login'))
    
    teacher_id = session['teacher_id']
    teacher = teacher_table(teacher_id)
    return render_template(
    'teacher/profile.html',
    teacher = teacher)
