from flask import Flask , Blueprint , redirect , url_for , render_template , request , flash , session
from datetime import datetime, date
from collections import defaultdict

from models.hod_model import hod_table
from models.hod_model import students_count
from models.hod_model import get_register_nos_by_year
from models.hod_model import dept_attendance_percentage
from models.hod_model import get_active_semester_for_hod
from models.hod_model import each_dept_std
from models.hod_model import teacher_lis
from models.hod_model import search_teachers
from models.hod_model import inst_to_teachers
from models.hod_model import check_teachers
from models.hod_model import teacher_data_for_edit
from models.hod_model import teacher_data_fro_update
from models.hod_model import timetable_data_for_teachers
from models.hod_model import delt_teach_for_hod
from models.hod_model import incharge_lis
from models.hod_model import search_incharge
from models.hod_model import check_incharge
from models.hod_model import check_class_assigned
from models.hod_model import inst_to_incharge
from models.hod_model import incharge_data_for_edit
from models.hod_model import incharge_data_fro_update
from models.hod_model import delt_incharge_for_hod
from models.hod_model import chech_update_data_incharge
from models.hod_model import each_year_std
from models.hod_model import active_sem_for_year
from models.hod_model import year_attendance
from models.hod_model import teacher_subject_map
from models.hod_model import insert_timetable
from models.hod_model import fetch_timetable
from models.hod_model import delete_existing_timetable
from models.hod_model import all_teachers_lis_for_sub
from models.hod_model import insert_subject_assign
from models.hod_model import fetch_assigned_subjects
from models.hod_model import delete_existing_subjects
from models.hod_model import hod_prf_data
from models.admin_model import dept_lis

from utils.hod_utils import get_hod
from utils.hod_utils import dept_overall_percentage
from utils.hod_utils import each_dept_std_claculation
from utils.hod_utils import count_teacher
from utils.hod_utils import teacher_timetable_for_profile
from utils.hod_utils import count_incharge
from utils.hod_utils import std_count_for_year
from utils.hod_utils import calcul_atend_for_year
from utils.hod_utils import absent_std
from utils.hod_utils import timetable_inst
from utils.hod_utils import sub_assign_to_tech

hod = Blueprint('hod', __name__, url_prefix='/hod')

@hod.route('/index', methods = ['GET', 'POST'])
def hod_index():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))
    
    hod_id = session['hod_id'].strip().lower()

    try:
        total_dept, hod_name, start_year, end_year = hod_table(hod_id)
        count, total_classes = get_hod(total_dept,start_year,end_year)

        today = date.today()
        today_date = today.strftime('%A')

        if count == 1:
            return redirect(url_for('hod.hod_dashboard'))
        elif count == 0:
            return redirect(url_for('auth.login')) 

        total_students = students_count(total_dept, start_year, end_year)
        active_sems = get_active_semester_for_hod(total_dept)
        if active_sems:
            start_dates = [row['start_date'] for row in active_sems]
            end_dates   = [row['end_date'] for row in active_sems]
        else:
            flash("Please Inform admin to Allocate Semester Duration Dates", 'error')
            return redirect(url_for('auth.login'))

        register_nos = get_register_nos_by_year(total_dept,start_year,end_year)

        rows = dept_attendance_percentage(min(start_dates),max(end_dates),register_nos)

        precent_percentage = dept_overall_percentage(rows)
        stnd_data = each_dept_std(total_dept, start_year, end_year)
        invdul_dept = each_dept_std_claculation(stnd_data,start_year,end_year)

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.login"))
    
    return render_template(
    'hod/hod_index.html',
    hod_name = hod_name,
    today = today,
    today_date = today_date,
    total_department = count,
    total_classes = total_classes,
    total_students = total_students,
    avg_percentage = precent_percentage,
    department = invdul_dept,
    )

@hod.route('/dashboard', methods = ["POST", "GET"])
def hod_dashboard():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))
    
    hod_id = session['hod_id'].strip().lower()
    try:
        total_dept, hod_name, start_year, end_year = hod_table(hod_id)
        # save once in session
        session['start_year'] = start_year
        session['end_year'] = end_year

        count, _ = get_hod(total_dept,start_year,end_year)
        
        if count == 1:
            mult = None
        else:
            mult = 1

        if request.method == "POST":
            department = request.form.get('department').strip().lower()
            session['department'] = department
        else:
            department = session.get('department')

        if not department:
            department = total_dept[0].strip().lower()
            session['department'] = department

        today = date.today()


        total_student = students_count([department],start_year,end_year)

        _, total_class = get_hod([department],start_year,end_year)

        active_sems = get_active_semester_for_hod([department])
        if active_sems:
            start_dates = [row['start_date'] for row in active_sems]
            end_dates   = [row['end_date'] for row in active_sems]
        else:
            flash("Please Inform admin to Allocate Semester Duration Dates", 'error')
            return redirect(url_for('auth.login'))
        
        register_nos = get_register_nos_by_year([department],start_year,end_year)

        rows = dept_attendance_percentage(min(start_dates),max(end_dates),register_nos)
        precent_percentage = dept_overall_percentage(rows)

        today_atd = dept_attendance_percentage(today, today,register_nos)
        today_percentage = dept_overall_percentage(today_atd)

        if start_year == 1 and end_year == 1:
            teacher = teacher_lis(start_year, end_year)
        else:
            teacher = teacher_lis(start_year, end_year, department)
        
        total_teacher, _ = count_teacher(teacher)

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.login"))
    
    return render_template(
    'hod/dashboard.html',
    total_classes = total_class,
    total_students= total_student,
    total_teachers = total_teacher,
    hod_name = hod_name,
    department = department,
    avg_percentage = precent_percentage ,
    mult = mult,
    semester_percentage = precent_percentage,  
    today_percentage = today_percentage,
    start_year = start_year,
    end_year = end_year
    )

@hod.route('/teacher/list', methods=["POST","GET"])
def teacher_list():
    if 'hod_id' not in session:
          return redirect(url_for('auth.login'))

    teach_data = None
    department = None

    try:
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))

        department = session.get('department').strip().lower()

        if start_year == 1 and end_year == 1:
            teacher = teacher_lis(start_year, end_year)
        else:
            teacher = teacher_lis(start_year, end_year, department)
        _, teach_data = count_teacher(teacher)

    except Exception as e:
        print("Error",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.hod_dashboard"))
    
    return render_template(
    'hod/teacher_list.html',
    teach_data = teach_data,
    department =department
    )

@hod.route('/action', methods=['GET', 'POST'])
def teacher_action():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        department = session.get('department').strip().lower()
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))

        teach_data=None
        department = None
        if request.method == "POST":
            action = request.form.get('action')
            department  = request.form.get('department').strip().lower()

            if action == 'search':
                search_data = request.form.get('search_data').strip().lower()
                if start_year == 1 and end_year == 1: 
                    teachers = search_teachers(search_data, start_year, end_year)
                else:
                    teachers = search_teachers(search_data, start_year, end_year, department)

                _, teach_data = count_teacher(teachers)
    except Exception as e:
        print("Error",e)
        flash("Something went wrong. Please try again.", "error")
        return(redirect(url_for("hod.teacher_list")))

    return render_template(
    'hod/teacher_list.html',
    teach_data=teach_data,
    department = department)

@hod.route('/add/teacher', methods=["POST"])
def add_teacher():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        action = request.form.get('action')
        department = session.get('department').strip().lower()
        hod_year = None
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))


        if action == 'open':
            if start_year == 1 and end_year == 1: 
                departments = dept_lis()
                hod_year = True
            else:
                departments = request.form.get('department').strip().upper()
                hod_year = False

            return render_template('hod/add_teacher.html',department=departments, hod_year = hod_year)

        if action == 'save':
            teacher_id = request.form.get('teacher_id', '').strip().lower()
            email      = request.form.get('email', '').strip().lower()
            name       = request.form.get('name', '').strip().lower()
            phone      = request.form.get('phone', '').strip().lower()
            department = request.form.get('department', '').strip().lower()
            gender     = request.form.get('gender', '').strip().lower()
            password   = request.form.get('password')
            experience = request.form.get('experience')
            teacher_year = request.form.get('teacher_year')

            if all([teacher_id, email, name, phone, department, gender, password, experience, teacher_year]):
                if not check_teachers(teacher_id, email, phone, department):
                    inst_to_teachers(
                        teacher_id, email, name, phone,
                        department, gender, password, experience, teacher_year
                    )
                    flash('Teacher Added Successfully!', 'success')
                else:
                    flash('Teacher Already Exists!', 'error')
            else:
                flash('All fields are required!', 'error')

            return render_template('hod/add_teacher.html', department = department.upper())

    except Exception as e:
        print("Error",e)
        flash("Something went wrong. Please try again.", "error")
        return(redirect(url_for("hod.teacher_list")))
    
@hod.route('/edit/teacher', methods = ["POST", "GET"])
def edit_teacher():
    if "hod_id" not in session:
        return redirect(url_for('auth.login'))
    try:
        action = request.form.get('action')
        department = session.get('department').strip().lower()
        teacher = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        experience = None
        teacher_year = None

        if action == 'edit':
            teacher_id = request.form.get('teacher_id', '').strip().lower()
            department = request.form.get('department','').strip().lower()
            teacher = teacher_data_for_edit(teacher_id, department)
            if teacher:
                email      = teacher['email']
                name       = teacher['name']
                phone      = teacher['phone']
                department = teacher['department']
                gender     = teacher['gender']
                password   = teacher['password']
                experience = teacher['experience']
                teacher_year = teacher['teacher_year']


            return render_template(
            "hod/edit_teacher.html",
            teacher_id = teacher_id,
            department = department,
            name = name,
            gender = gender,
            password = password,
            email = email,
            phone = phone,
            experience = experience,
            teacher_year = teacher_year)

        if action == "update":
            teacher_id = request.form.get('teacher_id', '').strip().lower()
            email      = request.form.get('email', '').strip().lower()
            name       = request.form.get('name', '').strip().lower()
            phone      = request.form.get('phone', '').strip().lower()
            department = request.form.get('department', '').strip().lower()
            gender     = request.form.get('gender', '').strip().lower()
            password   = request.form.get('password')
            experience = request.form.get('experience')
            teacher_year = request.form.get('teacher_year')

            teacher_data_fro_update(name, email, phone, experience, password, gender, teacher_year, teacher_id, department)
            flash('Successfully Updated!', 'success')
            return redirect(url_for('hod.teacher_list'))
        
    except Exception as e:
        print("Error",e)
        flash("Something went wrong. Please try again.", "error")
        return(redirect(url_for("hod.teacher_list")))
      
    return render_template("hod/edit_teacher.html")

@hod.route('/view/teacher', methods = ["POST", "GET"])
def view_teacher():
    if "hod_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        department = session.get('department').strip().lower()
        teacher = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        experience = None

        if action == 'view':
            teacher_id = request.form.get('teacher_id', '').strip().lower()
            department = request.form.get('department','').strip().lower()
            teacher = teacher_data_for_edit(teacher_id, department)
            if teacher:
                email      = teacher['email']
                name       = teacher['name']
                phone      = teacher['phone']
                department = teacher['department']
                gender     = teacher['gender']
                password   = teacher['password']
                experience = teacher['experience']

            timetable = timetable_data_for_teachers(teacher_id, department)
            subject, year = teacher_timetable_for_profile(timetable)

    except Exception as e:
        print("Error",e)
        flash("Something went wrong. Please try again.", "error")
        return(redirect(url_for("hod.teacher_list")))
    
    return render_template(
    "hod/view_teacher.html",
    teacher_id = teacher_id,
    department = department,
    name = name,
    gender = gender,
    password = password,
    email = email,
    phone = phone,
    experience = experience,
    subject_name = subject,
    year = year,) 

@hod.route("/delete/teacher", methods = ["POST", "GET"])
def delete_teacher():
    if "hod_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:

        action = request.form.get('action')

        teacher_id = None
        department = session.get('department').strip().lower()

        if action == 'delete':
            teacher_id = request.form.get('teacher_id').strip().lower()
            department = request.form.get('department').strip().lower()

            if teacher_id and department:
                delt_teach_for_hod(teacher_id, department)
                flash("Successfully Deleted!", "success")
                return redirect(url_for('hod.teacher_list'))

            else:
                flash("Teacher isn't Found!", 'danger')
                return redirect(url_for('hod.teacher_list'))
    except Exception as e:
        print("Error",e)
        flash("Something went wrong. Please try again.", "error")
        return(redirect(url_for("hod.teacher_list")))
    
    return render_template("hod/teacher_list.html")

@hod.route('/incharge/list', methods=["POST","GET"])
def incharge_list():
    if 'hod_id' not in session:
          return redirect(url_for('auth.login'))

    incharge_data = None
    try:
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))
        department = session.get('department').strip().lower()
        if request.method == "POST":
            department = request.form.get('department').strip().lower()
            session['department'] = department

        else:
            department = session['department'].strip().lower()

        if start_year == 1 and end_year == 1:
            incharge = incharge_lis(start_year, end_year)
        else:
            incharge = incharge_lis(start_year, end_year, department)

        _, incharge_data = count_incharge(incharge)

    except Exception as e:
        print("Error",e)
        flash("Something went wrong. Please try again.", "error")
        return(redirect(url_for("hod.incharge_list")))

    return render_template(
    'hod/incharge_list.html',
    incharge_data = incharge_data,
    department =department
    )

@hod.route('/incharge/action', methods=['GET', 'POST'])
def incharge_action():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))

        incharge_data = None
        department = None

        if request.method == "POST":
            action = request.form.get('action')
            department = request.form.get('department').strip().lower()

            if action == 'search':
                search_data = request.form.get('search_data').strip().lower()

                # 🔹 1st year HOD → common incharge
                if start_year == 1 and end_year == 1:
                    incharge = search_incharge(search_data, start_year, end_year)
                else:
                    incharge = search_incharge(search_data, start_year, end_year, department)

                _, incharge_data = count_incharge(incharge)

    except Exception as e:
        print("Error :", e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.incharge_list"))

    return render_template(
        'hod/incharge_list.html',
        incharge_data=incharge_data,
        department=department
    )

@hod.route('/add/incharge', methods=["POST"])
def add_incharge():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        action = request.form.get('action')
        department = session.get('department').strip().lower()
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))
        hod_year = None

        # 🔹 OPEN FORM
        if action == 'open':
            if start_year == 1 and end_year == 1:
                departments = dept_lis()   # all departments
                hod_year = True
            else:
                departments = request.form.get('department').strip().upper()
                hod_year = False

            return render_template(
                'hod/add_incharge.html',
                department=departments,
                hod_year=hod_year
            )

        # 🔹 SAVE INCHARGE
        if action == 'save':
            incharge_id = request.form.get('incharge_id', '').strip().lower()
            email       = request.form.get('email', '').strip().lower()
            name        = request.form.get('name', '').strip().lower()
            phone       = request.form.get('phone', '').strip().lower()
            department  = request.form.get('department', '').strip().lower()
            gender      = request.form.get('gender', '').strip().lower()
            password    = request.form.get('password')
            experience  = request.form.get('experience')
            year        = request.form.get('year')
            semester    = request.form.get('semester')
            incharge_year = request.form.get('incharge_year')

            if all([incharge_id, email, name, phone, department,
                    gender, password, experience, year, semester, incharge_year]):

                if check_incharge(incharge_id, email, phone, department):
                    flash("Incharge already exists (ID / Email / Phone)", "error")

                elif check_class_assigned(department, year, semester):
                    flash("Class already assigned to another incharge", "error")

                else:
                    inst_to_incharge(
                        incharge_id, email, name, phone,
                        department, gender, password,
                        experience, year, semester, incharge_year
                    )
                    flash("Incharge Added Successfully!", "success")
            else:
                flash("All fields are required!", "error")

            return render_template(
                'hod/add_incharge.html',
                department=department.upper()
            )

    except Exception as e:
        print("Error :", e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.incharge_list"))

@hod.route('/edit/incharge', methods = ["POST", "GET"])
def edit_incharge():
    if "hod_id" not in session:
        return redirect(url_for('auth.login'))
    try:
        action = request.form.get('action')
        department = session.get('department').strip().lower()
        incharge = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        experience = None
        year = None
        semester = None
        incharge_year =None

        if action == 'edit':
            incharge_id = request.form.get('incharge_id', '').strip().lower()
            department = request.form.get('department','').strip().lower()
            incharge = incharge_data_for_edit(incharge_id, department)
            if incharge:
                email      = incharge['email']
                name       = incharge['name']
                phone      = incharge['phone']
                department = incharge['department']
                gender     = incharge['gender']
                password   = incharge['password']
                experience = incharge['experience']
                year = incharge['year']
                semester = incharge['semester']
                incharge_year = incharge['incharge_year']

            return render_template(
            "hod/edit_incharge.html",
            incharge_id = incharge_id,
            department = department,
            name = name,
            gender = gender,
            password = password,
            email = email,
            phone = phone,
            experience = experience,
            year = year,
            semester =semester,
            incharge_year =incharge_year)

        if action == "update":
            incharge_id = request.form.get('incharge_id', '').strip().lower()
            email      = request.form.get('email', '').strip().lower()
            name       = request.form.get('name', '').strip().lower()
            phone      = request.form.get('phone', '').strip().lower()
            department = request.form.get('department', '').strip().lower()
            gender     = request.form.get('gender', '').strip().lower()
            password   = request.form.get('password')
            experience = request.form.get('experience')
            year = request.form.get('year')
            semester = request.form.get('semester')
            incharge_year = request.form.get('incharge_year')

            if not chech_update_data_incharge(year, semester, department, incharge_id):
                incharge_data_fro_update(name, email, phone, experience, password, gender, incharge_year, year, semester, incharge_id, department)
                flash('Successfully Updated!', 'success')
            else:
                flash("Class Is Already Assigned For Another Incharge", "error")
            return redirect(url_for('hod.incharge_list'))
        
    except Exception as e:
        print("Error :", e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.incharge_list"))
    
    return render_template("hod/edit_incharge.html")


@hod.route('/view/incharge', methods = ["POST", "GET"])
def view_incharge():
    if "hod_id" not in session:
        return redirect(url_for('auth.login'))
    try:
        action = request.form.get('action')
        department = session.get('department').strip().lower()
        incharge = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        experience = None

        if action == 'view':
            incharge_id = request.form.get('incharge_id', '').strip().lower()
            department = request.form.get('department','').strip().lower()
            incharge = incharge_data_for_edit(incharge_id, department)
            if incharge:
                email      = incharge['email']
                name       = incharge['name']
                phone      = incharge['phone']
                department = incharge['department']
                gender     = incharge['gender']
                password   = incharge['password']
                experience = incharge['experience']
                year = incharge['year']
                semester = incharge['semester']

    except Exception as e:
        print("Error :", e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.incharge_list"))
    
    return render_template(
    "hod/view_incharge.html",
    incharge_id = incharge_id,
    department = department,
    name = name,
    gender = gender,
    password = password,
    email = email,
    phone = phone,
    experience = experience,
    year = year,
    semester = semester)

@hod.route("/delete/incharge", methods = ["POST", "GET"])
def delete_incharge():
    if "hod_id" not in session:
        return redirect(url_for('auth.login'))

    try:
        action = request.form.get('action')
        department = session.get('department').strip().lower()
        incharge_id = None


        if action == 'delete':
            incharge_id = request.form.get('incharge_id')
            department = request.form.get('department')

            if incharge_id and department:
                delt_incharge_for_hod(incharge_id, department)
                flash("Successfully Deleted!", "success")
                return redirect(url_for('hod.incharge_list'))

            else:
                flash("incharge isn't Found!", 'error')
                return redirect(url_for('hod.incharge_list'))
            
    except Exception as e:
        print("Error :", e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.incharge_list"))
        
    return render_template("hod/incharge_list.html")

@hod.route("/attendance/report", methods=["GET", "POST"])
def attendance_report():
    if "hod_id" not in session:
        return redirect(url_for('auth.login'))

    try:
        department = session.get('department').strip().lower()
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))
        year = None
        std_count = None
        sem = None
        semester_precentage = None
        today_precentage =None
        absent = None
        total_absent = None
        today = date.today()
        day = today.strftime("%A")

        if start_year == 1 and end_year == 1:
            hod_year = 1
        else:
            hod_year = 2

        if request.method == "POST":
            action = request.form.get('action')

            if action == 'dept':
                department = request.form.get('department').strip().lower()
                session['department'] = department

            elif action == 'year':
                department = request.form.get('department').strip().lower()
                year = int(request.form.get('year'))
                today = date.today()

                session['department'] = department
                session['report_year'] = year

                std, sem, reg_no = each_year_std(department, year)
                std_count = std_count_for_year(std)

                active = active_sem_for_year(department, year, today)
                if active:
                    start_date = active['start_date']
                    end_date = active['end_date']

                    sem_attend = year_attendance(start_date, end_date, reg_no)
                    if sem_attend:
                        semester_precentage = calcul_atend_for_year(sem_attend)
                else:
                    semester_precentage = 0

                today_attend = year_attendance(today, today, reg_no)
                if today_attend:
                    today_precentage = calcul_atend_for_year(today_attend)
                else:
                    today_precentage = 0

                absent, total_absent = absent_std(today_attend)

    except Exception as e:
        print("Error :", e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.hod_dashboard"))
        
    return render_template(
        "hod/attendance_report.html",
        department=department.upper(),
        year=year,
        total_students = std_count,
        semester = sem,
        semester_percentage = semester_precentage,
        today_percentage = today_precentage,
        absent = absent,
        today = day,
        total_absent = total_absent,
        hod_year = hod_year
    )

@hod.route("/create/timetable", methods=["GET", "POST"])
def create_timetable():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        department = session.get("department").strip().lower()
        subjects = []
        timetable_data = {}
        year = semester = None
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))

        if start_year == 1 and end_year == 1:
            hod_year = 1
        else:
            hod_year = 2

        if request.method == "POST":
            year = int(request.form.get('year'))
            semester = int(request.form.get('semester'))
            action = request.form.get('action')

            if action == "load":
                try:
                    subjects = teacher_subject_map(semester, year, department)
                    timetable_data = fetch_timetable(department, year, semester)
                except Exception as e:
                    print("❌LOAD ERROR:", e)
                    flash("❌ Failed to load timetable", "error")

            elif action == "save":
                raw = request.form.to_dict()
                from collections import defaultdict
                timetable = defaultdict(dict)
                try:
                    for key, value in raw.items():
                        if key.startswith("timetable"):
                            _, day, period = key.replace("]", "").split("[")
                            timetable[day][int(period)] = value
                    try:
                        delete_existing_timetable(department, year, semester)
                        timetable_inst(timetable, insert_timetable, department, semester, year)
                        flash("Successfully Updated", 'success')
                    except Exception as db_e:
                        print("❌SAVE ERROR:", db_e)
                        flash("❌ Failed to save timetable", "error")
                    subjects = teacher_subject_map(semester, year, department)
                    timetable_data = fetch_timetable(department, year, semester)
                except Exception as parse_e:
                    print("❌PARSE ERROR:", parse_e)
                    flash("❌ Failed to parse form data", "error")
    except Exception as e:
        print("❌ERROR:", e)
        flash("Timetable Creation Failed. Please try again." , "error")
        return redirect(url_for("hod.hod_dashboard"))

    return render_template(
        "hod/create_timetable.html",
        department=department,
        subjects=subjects,
        timetable_data=timetable_data,
        year=year,
        semester=semester,
        hod_year = hod_year
    )

@hod.route('/subjects/assign', methods=["POST", "GET"])
def subject_assign():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        department = session.get('department').strip().lower()

        year = semester = None
        teachers = []
        num = 1
        action = None
        assigned_subjects = []
        start_year = int(session.get('start_year'))
        end_year   = int(session.get('end_year'))

        if start_year == 1 and end_year == 1:
            hod_year = 1
        else:
            hod_year = 2

        if request.method == "POST":
            action = request.form.get('action')
            year = int(request.form.get('year'))
            semester = int(request.form.get('semester'))

            if action == 'load':
                assigned_subjects = fetch_assigned_subjects(department, year, semester)
                teachers = all_teachers_lis_for_sub()

                # number of rows = db count or minimum 1
                num = len(assigned_subjects) if assigned_subjects else 1

            elif action == "save":
                raw = request.form.to_dict()
                subjects_data = defaultdict(dict)

                delete_existing_subjects(department, year, semester)
                sub_assign_to_tech(
                    raw,
                    subjects_data,
                    insert_subject_assign,
                    department,
                    year,
                    semester
                )

                flash("Successfully Assigned!", "success")

                # reload after save
                assigned_subjects = fetch_assigned_subjects(department, year, semester)
                teachers = all_teachers_lis_for_sub()
                num = len(assigned_subjects) if assigned_subjects else 1

    except Exception as e:
        print("❌ERROR:", e)
        flash("Subject Assign Failed. Please try again." , "error")
        return redirect(url_for("hod.hod_dashboard"))

    return render_template(
        'hod/subjects_assign.html',
        teachers=teachers,
        semester=semester,
        department=department,
        num=num,
        year=year,
        assigned_subjects=assigned_subjects,
        hod_year = hod_year
    )

@hod.route('/hod/profile')
def hod_profile():
    if 'hod_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        hod_id = session['hod_id'].strip().lower()
        total_dept, _, start_year, end_year = hod_table(hod_id)
        count,_ = get_hod(total_dept,start_year,end_year)

        if count == 1:
            mult = None
        else:
            mult = 1

        hod = hod_prf_data(hod_id)
        gender = hod['gender'].strip().lower()
        department = session.get('department').strip().lower()
        
    except Exception as e:
        print("Error :", e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("hod.hod_dashboard"))
    
    return render_template(
    'hod/hod_profile.html',
    hod = hod,
    gender = gender,
    department = department, 
    mult = mult)