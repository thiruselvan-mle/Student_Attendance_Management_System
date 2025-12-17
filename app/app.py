from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os 
import mysql.connector
from datetime import date, datetime, timedelta

Base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
Templates_dir = os.path.join(Base_dir, 'templates')
Static_dir = os.path.join(Base_dir, 'static')

app = Flask(__name__, template_folder=Templates_dir, static_folder=Static_dir)
app.secret_key = 'ekhfehfuiy8734yy48'

def get_db_connection():
    return mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'thiru@2006',
        database = 'student_attendance_management_system'
    )


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        user_id = request.form['user_id']
        password = request.form['password']
        conn = get_db_connection() 
        cursor = conn.cursor(dictionary=True)

        if role == 'student':
            cursor.execute("SELECT * FROM students WHERE register_no=%s AND password=%s",(user_id,password,))
            result = cursor.fetchone()
            if result:
                session['register_no']=result['register_no']
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid Register No Or Password!', 'danger')
        elif role == 'teacher':
            cursor.execute("SELECT * FROM teachers WHERE teacher_id=%s AND password=%s",(user_id,password,))
            result = cursor.fetchone()
            if result:
                session['teacher_id']=result['teacher_id']
                return redirect(url_for('teacher_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')

        elif role == 'incharge':
            cursor.execute("SELECT * FROM incharge WHERE incharge_id=%s AND password=%s",(user_id,password,))
            result = cursor.fetchone()
            if result:
                session['incharge_id']=result['incharge_id']
                return redirect(url_for('incharge_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')
           
        elif role == 'hod':
            cursor.execute("SELECT * FROM hod WHERE hod_id=%s AND password=%s",(user_id,password,))
            result = cursor.fetchone()
            if result:
                session['hod_id']=result['hod_id']
                return redirect(url_for('hod_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')
            
        elif role == 'admin':
            cursor.execute("SELECT * FROM admin WHERE admin_id=%s AND password=%s",(user_id,password,))
            result = cursor.fetchone()
            if result:
                session['admin_id']=result['admin_id']
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')

    return render_template('login.html')

@app.route('/student/dashboard', methods = ['GET', 'POST'])
def student_dashboard():
    if 'register_no' not in session:
        return redirect(url_for('login'))
    
    register_no = session['register_no']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT name, department, year, class FROM students WHERE register_no = %s",(register_no,))
    result = cursor.fetchone()

    if not result:
        return 'Student Not Found!'
    
    name, department, year, class_name = result['name'], result['department'], result['year'], result['class']

    cursor.execute("""
        SELECT p1, p2, p3, p4, p5, p6, p7
        FROM attendance
        WHERE student_id = %s
    """, (register_no,))

    rows = cursor.fetchall()

    total_present = 0
    total_absent = 0
    
    for row in rows:
        periods = [row['p1'], row['p2'], row['p3'], row['p4'], row['p5'], row['p6'], row['p7']]
        total_present += periods.count("present")
        total_absent  += periods.count("absent")

    total_periods = total_present + total_absent
    
    if total_periods > 0:
        present_percent = round((total_present / total_periods) * 100)
        absent_percent  = round((total_absent / total_periods) * 100)
    else:
        present_percent = 0
        absent_percent  = 0

    today = date.today().isoformat()

    cursor.execute("""
        SELECT p1, p2, p3, p4, p5, p6, p7
        FROM attendance
        WHERE student_id = %s AND date = %s
    """, (register_no, today))

    today_row = cursor.fetchone()

    if today_row:
        periods = list(today_row)
        p = periods.count("present")
        a = periods.count("absent")

        if a > p:
            today_status = "absent"
        else:
            today_status = "present"

    else:
        today_status = "Data Not Updated"
    

    cursor.execute("SELECT COUNT(DISTINCT date) AS total_days FROM attendance WHERE student_id = %s", (register_no,))
    total_days = cursor.fetchone()['total_days'] or 0


    conn.close()
    
    return render_template('student/dashboard.html',
        student_name=name,
        department=department,
        year=year,
        class_name=class_name,
        present_percent=present_percent,
        absent_percent=absent_percent,
        total_days=total_days,
        today_status=today_status
    )

def get_week_dates(start_date):
    return [start_date + timedelta(days=i) for i in range(5)]  


def get_week_attendance(register_no, start_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    week_data = []
    for day in get_week_dates(start_date):
        date_str = day.strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT p1,p2,p3,p4,p5,p6,p7
            FROM attendance
            WHERE student_id=%s AND date=%s
        """, (register_no, date_str))

        row = cursor.fetchone()
        periods = list(row.values()) if row else ["no-data"] * 7

        week_data.append({
            "date": day.strftime("%d/%m/%Y"),
            "periods": periods
        })

    conn.close()
    return week_data

def get_day_timetable(department, year, class_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT day, p1, p2, p3, p4, p5, p6, p7
        FROM timetable
        WHERE department=%s AND year=%s AND class_name=%s
    """, (department, year, class_name))

    data = cursor.fetchall()
    conn.close()

    timetable = {}
    for row in data:
        timetable[row['day']] = [
            row['p1'], row['p2'], row['p3'],
            row['p4'], row['p5'], row['p6'], row['p7']
        ]

    return timetable

@app.route('/student/get_week_attendance')
def get_week_attendance_api():
    if 'register_no' not in session:
        return jsonify({})

    register_no = session['register_no']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    cursor.execute("""
        SELECT department, year, class
        FROM students
        WHERE register_no=%s
    """, (register_no,))
    student = cursor.fetchone()

    department = student['department']
    year = student['year']
    class_name = student['class']

    timetable = get_day_timetable(department, year, class_name)

    base_date = datetime.strptime(request.args.get('date'), "%Y-%m-%d")
    monday = base_date - timedelta(days=base_date.weekday())

    response = {}

    for i in range(5): 
        day_date = monday + timedelta(days=i)
        day_name = day_date.strftime("%A")
        date_str = day_date.strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT p1,p2,p3,p4,p5,p6,p7
            FROM attendance
            WHERE student_id=%s AND date=%s
        """, (register_no, date_str))

        row = cursor.fetchone()
        attendance = list(row.values()) if row else ["no-data"] * 7
        subjects = timetable.get(day_name, [""] * 7)

        response[day_name] = {}
        for idx in range(7):
            response[day_name][idx+1] = {
                "status": attendance[idx],
                "subject": subjects[idx]
            }

    conn.close()
    return jsonify(response)

@app.route('/student/attendance_overview')
def student_attendance_overview():
    if 'register_no' not in session:
        return redirect(url_for('login'))

    today = datetime.today()
    monday = today - timedelta(days=today.weekday())

    return render_template(
        'student/attendance_overview.html',
        monday=monday.strftime("%Y-%m-%d"),
        week_start=monday.strftime("%d/%m/%Y"),
        week_end=(monday + timedelta(days=4)).strftime("%d/%m/%Y")
    )

def load_timetable(cursor, department, semester, class_name):
    cursor.execute("""
        SELECT day, p1,p2,p3,p4,p5,p6,p7
        FROM timetable
        WHERE department=%s AND semester=%s AND class_name=%s
    """, (department, semester, class_name))

    timetable = {}
    for row in cursor.fetchall():
        timetable[row['day']] = row

    return timetable

def get_subject_total_periods(cursor, student_id, department, semester, class_name):

    # Load timetable ONCE
    timetable = load_timetable(cursor, department, semester, class_name)

    cursor.execute("""
        SELECT date
        FROM attendance
        WHERE student_id=%s AND class_name=%s AND semester=%s
    """, (student_id, class_name, semester))

    data_date = cursor.fetchall()

    subject_total = {}

    for record in data_date:
        day_name = record['date'].strftime('%A')

        if day_name not in timetable:
            continue

        day_tt = timetable[day_name]

        for i in range(1, 8):
            subject = day_tt[f'p{i}']
            if subject:
                subject_total[subject] = subject_total.get(subject, 0) + 1

    return subject_total

def get_subject_present_count(cursor, student_id, subject_total, department, semester, class_name):


    timetable = load_timetable(cursor, department, semester, class_name)

    subject_present = {sub: 0 for sub in subject_total}

    cursor.execute("""
        SELECT date, p1,p2,p3,p4,p5,p6,p7
        FROM attendance
        WHERE student_id=%s
    """, (student_id,))

    for record in cursor.fetchall():
        day_name = record['date'].strftime('%A')

        if day_name not in timetable:
            continue

        day_tt = timetable[day_name]

        for i in range(1, 8):
            if record[f'p{i}'] == 'present':
                subject = day_tt[f'p{i}']
                if subject in subject_present:
                    subject_present[subject] += 1

    return subject_present

def get_subject_overview(cursor, student_id, department, semester, class_name):

    subject_total = get_subject_total_periods(
        cursor, student_id, department, semester, class_name
    )

    subject_present = get_subject_present_count(
        cursor, student_id, subject_total, department, semester, class_name
    )

    overview = []
    for i, subject in enumerate(subject_total, start=1):
        overview.append({
            "sno": i,
            "subject": subject,
            "total_periods": subject_total[subject],
            "total_present": subject_present.get(subject, 0)
        })

    return overview

@app.route("/student/subject_overview")
def subject_overview():
    if 'register_no' not in session:
        return redirect(url_for('login'))

    student_id = session['register_no']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT department, semester, class
        FROM students
        WHERE register_no=%s
    """, (student_id,))
    data = cursor.fetchone()

    department = data['department']
    semester = data['semester']
    class_name = data['class']

    overview = get_subject_overview(
        cursor, student_id, department, semester, class_name
    )

    return render_template(
        "student/subject_overview.html",
        overview=overview
    )



@app.route('/teacher/dashboard', methods = ['GET', 'POST'])
def teacher_dashboard():
    return render_template('teacher/dashboard.html')

@app.route('/incharge/dashboard', methods = ['GET', 'POST'])
def incharge_dashboard():
    return render_template('incharge/dashboard.html')

@app.route('/hod/dashboard', methods = ['GET', 'POST'])
def hod_dashboard():
    return render_template('hod/dashboard.html')

@app.route('/admin/dashboard', methods = ['GET', 'POST'])
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
