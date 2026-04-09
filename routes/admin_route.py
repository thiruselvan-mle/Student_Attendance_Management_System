from flask import Flask , Blueprint , redirect , url_for , render_template , request , flash , session, jsonify
from datetime import date, datetime
from collections import defaultdict

from models.admin_model import admin_table
from models.admin_model import dept_count
from models.admin_model import teacher_lis
from models.admin_model import student_lis
from models.admin_model import sem_date
from models.admin_model import avg_attend
from models.admin_model import get_semester_attendance_by_dept
from models.admin_model import get_today_attendance_by_dept
from models.admin_model import hod_lis
from models.admin_model import dept_lis
from models.admin_model import std_for_each_dept
from models.admin_model import chech_dept
from models.admin_model import inst_dept
from models.admin_model import delt_dept
from models.admin_model import check_hod
from models.admin_model import inst_hod
from models.admin_model import delt_hod
from models.admin_model import hod_data_for_view
from models.admin_model import update_hod_for_admin
from models.admin_model import incharge_data
from models.admin_model import incharge_data_for_search
from models.hod_model import check_incharge
from models.hod_model import check_class_assigned
from models.hod_model import inst_to_incharge
from models.hod_model import incharge_data_for_edit
from models.hod_model import chech_update_data_incharge
from models.hod_model import incharge_data_fro_update
from models.hod_model import delt_incharge_for_hod
from models.admin_model import teacher_data
from models.admin_model import teacher_data_for_search
from models.hod_model import check_teachers
from models.hod_model import inst_to_teachers
from models.hod_model import teacher_data_for_edit
from models.hod_model import timetable_data_for_teachers
from models.hod_model import teacher_data_fro_update
from models.hod_model import delt_teach_for_hod
from models.admin_model import student_data
from models.admin_model import student_data_for_search
from models.admin_model import check_students
from models.admin_model import inst_to_students
from models.admin_model import student_data_for_view
from models.admin_model import student_data_fro_update
from models.admin_model import delt_student_for_admin
from models.hod_model import each_year_std
from models.hod_model import active_sem_for_year
from models.hod_model import year_attendance
from models.admin_model import admin_prf_data
from models.admin_model import promote_std
from models.admin_model import update_std_year_sem
from models.admin_model import get_sem_duration
from models.admin_model import update_sem_duration
from models.admin_model import insert_sem_duration
from models.admin_model import update_sem_mast_year
from models.admin_model import year_from_sem_master
from models.admin_model import delt_passout_std
from models.incharge_model import get_semester_date
from models.admin_model import check_attendance_for_sem
from models.admin_model import check_attendance_lock_for_sem
from models.admin_model import delt_attned_for_sem
from models.admin_model import delt_attned_lock_for_sem

from utils.hod_utils import calcul_atend_for_year
from utils.admin_utils import merge_dept_and_students
from utils.hod_utils import teacher_timetable_for_profile
from utils.admin_utils import inst_excel_data_for_hod
from utils.admin_utils import inst_excel_data_for_incharge
from utils.admin_utils import inst_excel_data_for_teacher
from utils.admin_utils import inst_excel_data_for_student
from utils.hod_utils import std_count_for_year
from utils.hod_utils import absent_std
from utils.admin_utils import promote_std_sem_year
from utils.admin_utils import promote_semester_master
from utils.admin_utils import visualize_active_sem

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard', methods = ['GET', 'POST'])
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        admin_id = session.get('admin_id')
        today = date.today()
        admin = admin_table(admin_id)
        total_dept = dept_count()
        total_teacher = teacher_lis()
        total_student = student_lis()

        active_sems = sem_date()
        if active_sems:
            start_date = active_sems['start_date']
            end_date = active_sems['end_date']
            sem_data = avg_attend(start_date, end_date)
            sem_percentage = calcul_atend_for_year(sem_data)

        today_data = avg_attend(today, today)
        today_percentage = calcul_atend_for_year(today_data)

        semester_data = get_semester_attendance_by_dept(start_date, end_date)
        today_data = get_today_attendance_by_dept(today)

    
        semester_labels = [d['department'] for d in semester_data]
        semester_values = [d['percentage'] for d in semester_data]

        today_labels = [d['department'] for d in today_data]
        today_values = [d['percentage'] for d in today_data]

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.login"))

    return render_template(
    'admin/dashboard.html',
    admin = admin,
    total_dept = total_dept,
    total_teacher = total_teacher,
    total_student = total_student,
    sem_percentage = sem_percentage,
    today_percentage = today_percentage,
    semester_labels=semester_labels,
    semester_values=semester_values,
    today_labels=today_labels,
    today_values=today_values
    )

@admin.route('/department/access')
def department_management():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        department = dept_lis()
        dept_data = std_for_each_dept()
        merge_data = merge_dept_and_students(department, dept_data)

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template(
    'admin/department_management.html',
    departments = merge_data
    )

@admin.route('/add/department', methods = ["POST", "GET"])
def add_department():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    name = None
    code = None
    try:
        if request.method == "POST":
            name = request.form.get('department_name').strip().lower()
            code = request.form.get('department_code').strip().lower()

            if all([name,code]):
                if chech_dept(code):
                    flash("department Already Exists", "error")

                else:
                    inst_dept(code,name)
                    flash("Successfully Updated", 'success')

            else:
                flash("Please Give Required input", "error")

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.department_management"))
    
    return render_template('admin/add_department.html')

@admin.route('/delete/departments', methods = ["POST", "GET"])
def delete_department():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        if request.method == "POST":
            action = request.form.get('action')

            if action == 'delete':
                code = request.form.get('code').strip().lower()

                if code:
                    delt_dept(code)
                    flash("Successfully Deleted", 'success')
                else:
                    flash("something wrong", "error")

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.department_management"))
       
    return redirect(url_for('admin.department_management'))

@admin.route('/hod/access')
def hod_management():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:

        hod = hod_lis()
    
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template(
    'admin/hod_management.html',
    hods = hod
    )

@admin.route('/add/hod', methods = ["POST", "GET"])
def add_hod():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
     
    try:
        dept = dept_lis()
        action = request.form.get('action')
        msg = None
        if action == 'excel':
            file = request.files.get("hod_excel")
            try:
                msg, category = inst_excel_data_for_hod(inst_hod, file, check_hod)
                flash(msg, category)

            except Exception as e:
                flash(f"Excel upload failed: {e}", "error")

            return redirect(url_for("admin.add_hod"))

        if action == 'manual':
            hod_id = request.form.get('hod_id').strip().lower()
            name = request.form.get('name').strip().lower()
            email = request.form.   get('email').strip().lower()
            phone = request.form.get('phone').strip().lower()
            gender = request.form.get('gender').strip().lower()
            department = request.form.get('department').strip().lower()
            experience = request.form.get('experience')
            password = request.form.get('password')
            start_year = request.form.get('start_year')
            end_year = request.form.get('end_year')

            if all([hod_id, name, email, phone, experience, password, gender, department, start_year, end_year]):
                if not check_hod(department, hod_id):
                    inst_hod(hod_id, name, email, phone, experience, password, gender, department, start_year, end_year)
                    flash("Successfully Added", 'success')
                else:
                    flash("HOD Already Assigned to this Department", "error")
            else:
                flash("Some Input are Null", 'error')

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.hod_management"))
    
    return render_template(
    'admin/add_hod.html',
    departments = dept
    )

@admin.route('/hod/actions', methods = ["POST", "GET"])
def hod_action():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
     
    try:
        action = request.form.get('action')
        hod_id = request.form.get('hod_id')
        department = request.form.get('department').strip().lower()

        if action == 'view':
            hod = hod_data_for_view(hod_id, department)
            return render_template('admin/view_hod.html', hod = hod)

        if action == 'edit':
            hod = hod_data_for_view(hod_id, department)
            return render_template('admin/edit_hod.html',hod = hod)

        if action == 'update':
            hod_id = request.form.get('hod_id').strip().lower()
            name = request.form.get('name').strip().lower()
            gender = request.form.get('gender').strip().lower()
            email = request.form.get('email').strip().lower()
            phone = request.form.get('phone')
            department = request.form.get('department').strip().lower()
            experience = request.form.get('experience')
            password = request.form.get('password')
            start_year = request.form.get('start_year')
            end_year = request.form.get('end_year')

            if all([hod_id, name, gender, email, phone, department, experience, password,start_year,end_year]):
                update_hod_for_admin(name, gender, email, phone, experience,start_year,end_year, password, hod_id, department)
                flash("Successfully Updated", 'success')
            else:
                flash("Some input are Null", 'error')
            return redirect(url_for('admin.hod_management'))

        if action == 'delete':
            if all([hod_id,department]):
                delt_hod(hod_id, department)
                flash("successfully Deleted", "success")

            else:
                flash("Some Input are Null", "error")

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.hod_management"))
    
    return redirect(url_for('admin.hod_management')) 

@admin.route('/incharge/management', methods = ["POST", "GET"])
def incharge_management():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        incharge = incharge_data()

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template("admin/incharge_management.html",incharge = incharge)

@admin.route('/search/incharge', methods = ["POST", "GET"])
def incharge_search():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        if action == 'search':
            search_data = request.form.get('search_data').strip().lower()
            incharge = incharge_data_for_search(search_data)

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.incharge_management"))
    
    return render_template("admin/incharge_management.html",incharge = incharge)

@admin.route('/add/incharge', methods=["POST", "GET"])
def add_incharge():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = None
        msg = None
        category = None
        departments = dept_lis()

        if request.method == "POST":
            action = request.form.get('action')

            if action == 'excel':  
                file = request.files.get("incharge_excel")
                try:
                    msg, category = inst_excel_data_for_incharge(check_class_assigned, inst_to_incharge, file, check_incharge)
                    flash(msg, category)

                except Exception as e:
                    flash(f"Excel upload failed: {e}", "error")

                return redirect(url_for("admin.add_incharge"))

            if action == 'manual':
                incharge_id = request.form.get('incharge_id', '').strip().lower()
                email      = request.form.get('email', '').strip().lower()
                name       = request.form.get('name', '').strip().lower()
                phone      = request.form.get('phone', '').strip().lower()
                department = request.form.get('department', '').strip().lower()
                gender     = request.form.get('gender', '').strip().lower()
                password   = request.form.get('password')
                experience   = request.form.get('experience')
                year   = request.form.get('year')
                semester   = request.form.get('semester')
                incharge_year = request.form.get("incharge_year")

                if all([incharge_id, email, name, phone, department, gender, password, experience, year, semester, incharge_year]):
                    if check_incharge(incharge_id, email, phone, department):
                        flash("Incharge already exists (ID / Email / Phone)", "error")

                    elif check_class_assigned(department, year, semester):
                        flash("Class already assigned to another incharge", "error")

                    else:
                        inst_to_incharge(incharge_id, email, name, phone,department, gender, password, experience, year, semester, incharge_year)
                        flash('incharge Added Successfully!', 'success')
                else:
                    flash('All fields are required!', 'error')
                return redirect(url_for('admin.add_incharge'))
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.incharge_management"))
    
    return render_template('admin/add_incharge.html', departments = departments)

@admin.route('/view/incharge', methods = ["POST", "GET"])
def view_incharge():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
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
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.incharge_management"))
    
    return render_template(
    "admin/view_incharge.html",
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

@admin.route('/edit/incharge', methods = ["POST", "GET"])
def edit_incharge():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
     
    try:
        action = request.form.get('action')
        incharge = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        experience = None
        year = None
        semester = None

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
                incharge_year=incharge['incharge_year']

            return render_template(
            "admin/edit_incharge.html",
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
            incharge_year=incharge_year)

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
            return redirect(url_for('admin.incharge_management'))

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.incharge_management"))
        
    return render_template("admin/edit_incharge.html")

@admin.route("/delete/incharge", methods = ["POST", "GET"])
def delete_incharge():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        department = None
        incharge_id = None


        if action == 'delete':
            incharge_id = request.form.get('incharge_id').strip().lower()
            department = request.form.get('department').strip().lower()

            if incharge_id and department:
                delt_incharge_for_hod(incharge_id, department)
                flash("Successfully Deleted!", "success")

            else:
                flash("incharge isn't Found!", 'danger')

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.incharge_management"))
     
    return redirect(url_for('admin.incharge_management'))
    
@admin.route('/teacher/management', methods = ["POST", "GET"])
def teacher_management():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        teacher = teacher_data()
    
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template("admin/teacher_management.html",teachers = teacher)

@admin.route('/teacher/search', methods = ["POST", "GET"])
def teacher_search():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        if action == 'search':
            search_data = request.form.get('search_data').strip().lower()
            teacher = teacher_data_for_search(search_data)

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.teacher_management"))
    
    return render_template("admin/teacher_management.html",teachers = teacher)

@admin.route('/add/teacher', methods=["GET", "POST"])
def add_teacher():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        action = None
        msg = None
        category = None
        departments = dept_lis()

        if request.method == "POST":
            action = request.form.get('action')

            if action == 'excel':  
                file = request.files.get("teacher_excel")
                try:
                    msg, category = inst_excel_data_for_teacher(inst_to_teachers, file, check_teachers)
                    flash(msg, category)

                except Exception as e:
                    flash(f"Excel upload failed: {e}", "error")

                return redirect(url_for('admin.add_teacher'))
            
            if action == 'manual':
                teacher_id = request.form.get('teacher_id', '').strip().lower()
                email      = request.form.get('email', '').strip().lower()
                name       = request.form.get('name', '').strip().lower()
                phone      = request.form.get('phone', '').strip().lower()
                department = request.form.get('department', '').strip().lower()
                gender     = request.form.get('gender', '').strip().lower()
                password   = request.form.get('password')
                experience = request.form.get('experience')
                teacher_year = request.form.get('teacher_year')

                if all([teacher_id, email, name, phone, department, gender, password, experience,teacher_year]):
                    if not check_teachers(teacher_id, email, phone, department):
                        inst_to_teachers(
                            teacher_id, email, name, phone,
                            department, gender, password, experience,teacher_year
                        )
                        flash('Teacher Added Successfully!', 'success')
                    else:
                        flash('Teacher Already Exists!', 'error')
                else:
                    flash('All fields are required!', 'error')
                return redirect(url_for('admin.add_teacher'))

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.teacher_management"))
    
    return render_template('admin/add_teacher.html', departments = departments )

@admin.route('/view/teacher', methods = ["POST", "GET"])
def view_teacher():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
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
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.teacher_management"))
    
    return render_template(
    "admin/view_teacher.html",
    teacher_id = teacher_id,
    department = department,
    name = name,
    gender = gender,
    password = password,
    email = email,
    phone = phone,
    experience = experience,
    subject_name = subject,
    year = year)

@admin.route('/edit/teacher', methods = ["POST", "GET"])
def edit_teacher():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        department = None
        teacher = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        experience = None
        
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
            "admin/edit_teacher.html",
            teacher_id = teacher_id,
            department = department,
            name = name,
            gender = gender,
            password = password,
            email = email,
            phone = phone,
            experience = experience,
            teacher_year=teacher_year)

        if action == "update":
            teacher_id = request.form.get('teacher_id', '').strip().lower()
            email      = request.form.get('email', '').strip().lower()
            name       = request.form.get('name', '').strip().lower()
            phone      = request.form.get('phone', '').strip().lower()
            department = request.form.get('department', '').strip().lower()
            gender     = request.form.get('gender', '').strip().lower()
            password   = request.form.get('password')
            experience = request.form.get('experience')
            teacher_year= request.form.get('teacher_year')

            teacher_data_fro_update(name, email, phone, experience, password, gender,teacher_year, teacher_id, department)
            flash('Successfully Updated!', 'success')
            return redirect(url_for('admin.teacher_management'))
    
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.teacher_management"))
    
    return render_template("admin/edit_teacher.html")

@admin.route("/delete/teacher", methods = ["POST", "GET"])
def delete_teacher():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')

        teacher_id = None
        department = None

        if action == 'delete':
            teacher_id = request.form.get('teacher_id').strip().lower()
            department = request.form.get('department').strip().lower()

            if teacher_id and department:
                delt_teach_for_hod(teacher_id, department)
                flash("Successfully Deleted!", "success")

            else:
                flash("Teacher isn't Found!", 'danger')
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.teacher_management"))
              
    return redirect(url_for('admin.teacher_management'))

@admin.route('/student/management', methods = ["POST", "GET"])
def student_management():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        students = student_data()
    
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template("admin/student_management.html",students = students)

@admin.route('/student/search', methods = ["POST", "GET"])
def student_search():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        if action == 'search':
            search_data = request.form.get('search_data')
            student = student_data_for_search(search_data)
    
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.student_management"))
    
    return render_template("admin/student_management.html",students = student)

@admin.route('/add/student', methods=["GET", "POST"])
def add_student():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        action = None
        msg = None
        category = None
        departments = dept_lis()

        if request.method == "POST":
            action = request.form.get('action')

            if action == 'excel':  
                file = request.files.get("student_excel")
                try:
                    msg, category = inst_excel_data_for_student(inst_to_students, file, check_students)
                    flash(msg, category)

                except Exception as e:
                    flash(f"Excel upload failed: {e}", "error")

                return redirect(url_for('admin.add_student'))
            
            if action == 'manual':
                register_no = request.form.get('register_no', '').strip().lower()
                email      = request.form.get('email', '').strip().lower()
                name       = request.form.get('name', '').strip().lower()
                phone      = request.form.get('phone', '').strip().lower()
                department = request.form.get('department', '').strip().lower()
                gender     = request.form.get('gender', '').strip().lower()
                password   = request.form.get('password')
                year = request.form.get('year')
                semester = request.form.get('semester')
                dob = request.form.get('dob')
                admission_year = request.form.get('admission_year')
                academic_year = request.form.get('academic_year').strip()

                if all([register_no, email, name, phone, department, gender, password, year, semester, dob, admission_year, academic_year]):
                    if not check_students(register_no, phone, email):
                        inst_to_students(
                            register_no, email, name, phone, department, gender, password,
                            year, semester, dob, admission_year, academic_year
                        )
                        flash('Student Added Successfully!', 'success')
                    else:
                        flash('Student Already Exists!', 'error')
                else:
                    flash('All fields are required!', 'error')
                return redirect(url_for('admin.add_student'))
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.student_management"))
    
    return render_template('admin/add_student.html', departments = departments )

@admin.route('/view/student', methods = ["POST", "GET"])
def view_student():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        student = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        semester = None
        year=None
        admission_year = None
        academic_year = None
        dob = None

        if action == 'view':
            register_no = request.form.get('register_no', '').strip().lower()
            student = student_data_for_view(register_no)
            if student:
                email      = student['email']
                name       = student['name']
                phone      = student['phone']
                department = student['department']
                gender     = student['gender']
                password   = student['password']
                dob        = student['dob']
                admission_year = student['admission_year']
                academic_year = student['academic_year']
                semester = student['semester']
                year = student['year']
            
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.student_management"))
    
    return render_template(
    "admin/view_student.html",
    register_no = register_no,
    department = department,
    name = name,
    gender = gender,
    password = password,
    email = email,
    dob = dob,
    phone = phone,
    semester = semester,
    academic_year = academic_year,
    admission_year = admission_year,
    year = year)

@admin.route('/edit/student', methods = ["POST", "GET"])
def edit_student():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')
        departments = dept_lis()
        department = None
        student = None
        email      = None
        name       = None
        phone      = None
        gender     = None
        password   = None
        semester = None
        year=None
        admission_year = None
        academic_year = None
        dob = None

        if action == 'edit':
            register_no = request.form.get('register_no', '').strip().lower()
            student = student_data_for_view(register_no)
            if student:
                email      = student['email']
                name       = student['name']
                phone      = student['phone']
                department = student['department']
                gender     = student['gender']
                password   = student['password']
                dob        = student['dob']
                admission_year = student['admission_year']
                academic_year = student['academic_year']
                semester = student['semester']
                year = student['year']

            return render_template(
            "admin/edit_student.html",
            register_no = register_no,
            department = department,
            name = name,
            gender = gender,
            password = password,
            email = email,
            dob = dob,
            phone = phone,
            semester = semester,
            academic_year = academic_year,
            admission_year = admission_year,
            year = year,
            departments = departments)

        if action == "update":
            register_no = request.form.get('register_no', '').strip().lower()
            email      = request.form.get('email', '').strip().lower()
            name       = request.form.get('name', '').strip().lower()
            phone      = request.form.get('phone', '').strip().lower()
            department = request.form.get('department', '').strip().lower()
            gender     = request.form.get('gender', '').strip().lower()
            password   = request.form.get('password')
            year = request.form.get('year')
            semester = request.form.get('semester')
            dob = request.form.get('dob')
            admission_year = request.form.get('admission_year')
            academic_year = request.form.get('academic_year').strip()
            
            student_data_fro_update(register_no, email, name, phone, department, gender, password, dob,
            year, semester, admission_year, academic_year)
            flash('Successfully Updated!', 'success')
            return redirect(url_for('admin.student_management'))
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.student_management"))
     
    return render_template("admin/edit_student.html")

@admin.route("/delete/student", methods = ["POST", "GET"])
def delete_student():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))
    
    try:
        action = request.form.get('action')

        register_no = None

        if action == 'delete':
            register_no = request.form.get('register_no').strip().lower()

            if register_no:
                delt_student_for_admin(register_no)
                flash("Successfully Deleted!", "success")

            else:
                flash("Student isn't Found!", 'danger')
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.student_management"))
             
    return redirect(url_for('admin.student_management'))

@admin.route("/attendance/report", methods=["GET", "POST"])
def attendance_report():
    if "admin_id" not in session:
        return redirect(url_for('auth.login'))

    try:
        departments = dept_lis()
        department = None
        year = None
        std_count = None
        sem = None
        semester_precentage = None
        today_precentage =None
        absent = None
        total_absent = None
        today = date.today()
        day = today.strftime("%A")

        if request.method == "POST":
            action = request.form.get('action')

            if action == 'dept':
                department = request.form.get('department').strip().lower()

            elif action == 'year':
                department = request.form.get('department').strip().lower()
                year = int(request.form.get('year'))
                today = date.today()

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
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template(
        "admin/attendance_report.html",
        departments=departments,
        department=department,
        year=year,
        total_students = std_count,
        semester = sem,
        semester_percentage = semester_precentage,
        today_percentage = today_precentage,
        absent = absent,
        today = day,
        total_absent = total_absent
    )

@admin.route('/sem/duration', methods=["GET", "POST"])
def semester_duration():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        departments = dept_lis() 
        rows = year_from_sem_master()
        active_sem = visualize_active_sem(rows, get_semester_date)
        if request.method == 'POST':
            year = int(request.form.get('year'))
            semester = int(request.form.get('semester'))
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            if not all([year, semester, start_date, end_date]):
                flash("Please fill all fields!", "danger")
                return redirect(url_for('admin.semester_duration'))

            existing = get_sem_duration(year, semester)

            if existing:
                update_sem_duration(year, semester, start_date, end_date)
            else:
                insert_sem_duration(year, semester, start_date, end_date)

            flash("Semester duration saved successfully!", "success")
            return redirect(url_for('admin.semester_duration'))

    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template(
        "admin/semester_master.html",
        departments = departments,
        active_sem_data = active_sem
    )

@admin.route('/sem/get', methods=['GET'])
def get_sem_ajax():
    if 'admin_id' not in session:
        return jsonify({"exists": False, "error": "Unauthorized"}), 401
    
    try:
        # 1. Get parameters safely
        year = request.args.get('year')
        semester = request.args.get('semester')

        if not year or not semester:
            return jsonify({"exists": False, "message": "Missing year or semester"})

        # 2. Call the model
        existing = get_sem_duration(int(year), int(semester))

        if existing:
            return jsonify({
                "exists": True,
                "start_date": existing['start_date'].strftime('%Y-%m-%d'),
                "end_date": existing['end_date'].strftime('%Y-%m-%d')
            })

        return jsonify({"exists": False})
    
    except Exception as e:
        print("AJAX Error :", e)
        # CRITICAL: Return JSON error, NOT a redirect
        return jsonify({"exists": False, "error": str(e)}), 500
    
@admin.route('/admin/profile', methods = ["GET","POST"])
def admin_profile():
    if 'admin_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        admin_id = session['admin_id']
        admin = admin_prf_data(admin_id)
    
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template(
    'admin/admin_profile.html',
    admin = admin)

@admin.route("/verify_password", methods=["POST"])
def verify_admin_password():
    if "admin_id" not in session:
        return jsonify({"success": False}), 401

    try:
        data = request.get_json()
        password = data.get("password")

        admin_id = session["admin_id"]
        admin = admin_table(admin_id)

        if not admin:
            return jsonify({"success": False})

        if admin["password"] != password:  
            return jsonify({"success": False})
    except Exception as e:
        print("Error :",e)
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("admin.admin_profile"))
    
    return jsonify({"success": True})


@admin.route("/promote_students", methods=["POST"])
def promote_students():
    if 'admin_id' not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:
        current_year = date.today().year

        students = promote_std()
        passout_std_list = promote_std_sem_year(students, update_std_year_sem)
        attend_data = check_attendance_for_sem()
        attend_lock_data = check_attendance_lock_for_sem()

        if passout_std_list:
            delt_passout_std()

        if attend_data:
            delt_attned_for_sem()

        if attend_lock_data:
            delt_attned_lock_for_sem()

        sem_data = year_from_sem_master()
        promote_semester_master(sem_data, current_year, update_sem_mast_year)

        return jsonify({
            "success": True,
            "message": "Successfully Promoted!"
        }), 200

    except Exception as e:
        print("❌ PROMOTION ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Promotion failed",
        }), 500
