from database.db_connection import get_db_connection
from extensions import cache # extensions-ல் இருந்து cache-ஐ இறக்குமதி செய்யவும்

# --- CACHE POTTA FUNCTIONS (Static Data) ---

@cache.memoize(timeout=600) # 10 நிமிடங்கள் Cache-ல் இருக்கும்
def incharge_table(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM incharge WHERE incharge_id = %s",(user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=600)
def students_list(semester, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT register_no, gender FROM students WHERE semester = %s AND department =%s ORDER BY register_no",(semester, department))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# --- CACHE PODATHA FUNCTIONS (Real-time Attendance Data) ---

def attendance_list(register_no):
    # அட்டெண்டன்ஸ் டேட்டா அடிக்கடி மாறும் என்பதால் இதற்கு Cache தேவையில்லை
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if not register_no:
        return [] 
    try:
        format_string = ','.join(['%s'] * len(register_no))
        query = f"SELECT register_no, name, status FROM attendance WHERE register_no IN ({format_string})"
        cursor.execute(query,tuple(register_no))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# --- CACHE POTTA FUNCTIONS (Timetable - Static) ---

@cache.memoize(timeout=600)
def load_cls_timetable(semester, department, day):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM timetable WHERE semester = %s AND department =%s AND day = %s",
        (semester, department, day))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# --- DATABASE UPDATES (No Cache) ---

def update_attendance(register_no, name, department, subject_name, subject_code, teacher_id, attendance_date, period_no, status, marked_by):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("UPDATE attendance SET status = %s , marked_by =%s WHERE register_no  = %s AND name = %s AND department =%s AND subject_name =%s AND subject_code = %s AND teacher_id = %s AND attendance_date =%s AND period_no=%s",(status, marked_by, register_no, name, department, subject_name, subject_code, teacher_id, attendance_date, period_no))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def update_attendance_lock(attendance_date, period_no, department, semester, subject_code, marked_by, role, teacher_id):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("UPDATE attendance_lock SET locked_by = %s , role = %s WHERE attendance_date=%s AND period_no=%s AND department=%s AND semester=%s AND subject_code=%s AND teacher_id=%s",
        ( marked_by,  role, attendance_date, period_no, department, semester, subject_code, teacher_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# --- CACHE POTTA FUNCTIONS (Full Timetable) ---

@cache.memoize(timeout=600)
def incharege_timetable(semester, department):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM timetable WHERE semester=%s AND department=%s",
        (semester, department ))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# --- REPORTS (Real-time - No Cache) ---

def current_month_list(month_start,month_end,register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if not register_no:
        return [] 
    try:
        format_string = ','.join(['%s'] * len(register_no))
        query = f"SELECT register_no, name, status FROM attendance WHERE attendance_date BETWEEN %s AND %s AND register_no IN ({format_string})"
        values = [month_start,month_end] +register_no
        cursor.execute(query, values)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# --- CACHE POTTA FUNCTIONS (Sem Dates) ---

@cache.memoize(timeout=600)
def get_semester_date(semester, department, year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM semester_master WHERE semester = %s AND department = %s AND year=%s AND CURDATE() BETWEEN start_date AND end_date LIMIT 1",(semester,department,year))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()