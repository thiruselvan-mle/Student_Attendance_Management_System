from flask import Flask , Blueprint , redirect , url_for , render_template , request , flash , session
from datetime import date, datetime
import calendar

from models.incharge_model import incharge_table
from models.incharge_model import students_list
from models.incharge_model import load_cls_timetable
from models.incharge_model import attendance_list
from models.incharge_model import incharege_timetable
from models.incharge_model import current_month_list

from utils.incharge_utils import calculate_percentage
from utils.incharge_utils import incharge_shedule
from utils.incharge_utils import today_incharge_periods
from utils.incharge_utils import count_students
from utils.incharge_utils import load_incharge_timetable
from utils.incharge_utils import month_calculation
from utils.incharge_utils import students_monthly_report

incharge = Blueprint('incharge', __name__, url_prefix='/incharge')

@incharge.route('/dashboard', methods = ['GET', 'POST'])
def incharge_dashboard():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))
    
    incharge_id = session['incharge_id']
    incharge = incharge_table(incharge_id)
    class_name = incharge['class_name']
    semester = incharge['semester']
    department = incharge['department']

    students = students_list(class_name, semester, department)
    register_no = [s['register_no'] for s in students]
    gender = [g['gender'] for g in students]
    total_count, male_count, female_count = count_students(register_no, gender)
    attendance = attendance_list(register_no)
    overall_percentage = calculate_percentage(attendance)
    today = date.today()
    day = today.strftime("%A")

    incharge_timetable = load_cls_timetable(class_name, semester, department, day)
    shedule = incharge_shedule(incharge_timetable)
    today_periods = today_incharge_periods(shedule)

    return render_template(
    'incharge/dashboard.html',
    incharge = incharge,
    male = male_count,
    female = female_count,
    total_students = total_count,
    overall_percentage = overall_percentage,
    today_periods = today_periods)

@incharge.route('/incahrge/timetable', methods = ["GET","POST"])
def incharge_timetable():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))
    
    incharge_id = session['incharge_id']
    incharge = incharge_table(incharge_id)
    department = incharge['department']
    class_name = incharge['class_name']
    semester = incharge['semester']
    year = incharge['year']
    rows = incharege_timetable(class_name, semester, department)
    timetable = load_incharge_timetable(rows)


    return render_template(
    'incharge/timetable.html',
    year = year,
    class_name = class_name,
    timetable =timetable
    )

@incharge.route("/monthly/report/")
def monthly_report():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))
    
    incharge_id = session['incharge_id']
    incharge = incharge_table(incharge_id)
    department = incharge['department']
    class_name = incharge['class_name']
    semester = incharge['semester']
    year = incharge['year']

    students = students_list(class_name, semester, department)
    rows = [s['register_no'] for s in students]

    today = date.today()
    current_year = today.year

    selected_month = int(request.args.get('month', date.today().month))
    month_name = calendar.month_name[selected_month]

    month_start, month_end = month_calculation(selected_month,today,current_year)
    
    lst = current_month_list(month_start,month_end,rows)
    reports, total_days = students_monthly_report(lst)
    

    return render_template(
    "incharge/monthly_report.html",
    department = department,
    month = month_name,
    semester = semester,
    year = year,
    today = today,
    reports = reports,
    total_days = total_days,
    current_year = current_year
    )


@incharge.route("/incharge/profile/")
def incharge_profile():
    if "incharge_id" not in session:
        return redirect(url_for('auth.login'))
    
    incharge_id = session['incharge_id']
    incharge = incharge_table(incharge_id)
    return render_template(
    'incharge/profile.html',
    incharge = incharge)
