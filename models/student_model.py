from database.db_connection import get_db_connection

def dashboard_student(register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM students WHERE register_no = %s",
        (register_no,))
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def dashboard_attendance(register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT attendance_date, status, period_no FROM attendance WHERE register_no = %s""", (register_no,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def dashboard_today_status(register_no, today):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT status FROM attendance WHERE register_no = %s AND attendance_date = %s""", (register_no, today))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
    
def dashboard_total_days(register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(DISTINCT attendance_date) AS total_days FROM attendance WHERE register_no = %s AND DAYOFWEEK(attendance_date) NOT IN (1,7)", 
        (register_no,))
        row = cursor.fetchone()
        return row['total_days'] if row and row['total_days'] else 0

    finally:
        cursor.close()
        conn.close()

def get_timetable(department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT day, period_no, subject_name FROM timetable WHERE department=%s AND year=%s AND semester=%s ORDER BY day, period_no """,  
        (department, year, semester))
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()


def get_active_semester(department , year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT semester, start_date, end_date FROM semester_master WHERE department = %s AND year=%s AND status='active' LIMIT 1""",
        (department, year))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

def student_day_attendance(register_no, date_str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT period_no, status FROM attendance WHERE register_no=%s AND attendance_date=%s ORDER BY period_no""", 
        (register_no, date_str))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
