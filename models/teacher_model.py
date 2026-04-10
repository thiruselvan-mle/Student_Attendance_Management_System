from database.db_connection import get_db_connection

def teacher_table(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM teachers WHERE teacher_id = %s", (user_id,))
        return cursor.fetchone()

    finally: 
        cursor.close()
        conn.close()

def teacher_class(teacher_id, day):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT period_no, subject_name, department, semester, year, subject_code, teacher_id FROM timetable WHERE teacher_id = %s AND day = %s  ORDER BY period_no """, 
        (teacher_id, day))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def get_student_list(year, department, semester):
    conn = get_db_connection()
    cursor =conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT register_no, name FROM students WHERE year=%s AND department=%s AND semester=%s",
        (year, department, semester))
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def insrt_attendance_tabel(register_no, name, department, subject_name, subject_code, teacher_id, attendance_date, period_no, status, marked_by):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("INSERT INTO attendance (register_no, name, department, subject_name, subject_code, teacher_id, attendance_date, period_no, status, marked_by )  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (register_no, name, department, subject_name, subject_code, teacher_id, attendance_date, period_no, status, marked_by))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def insrt_lock(attendance_date, period_no, department, semester, subject_code, marked_by, role, teacher_id):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("INSERT INTO attendance_lock (attendance_date, period_no, department, semester, subject_code, locked_by, role, teacher_id )  VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
        ( attendance_date, period_no, department, semester, subject_code, marked_by, role, teacher_id))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def is_attendance_locked(attendance_date, period_no, department, semester, subject_code, teacher_id):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT 1 FROM attendance_lock WHERE attendance_date =%s AND period_no =%s AND department=%s AND semester=%s AND subject_code=%s AND teacher_id=%s",
        ( attendance_date, period_no, department, semester, subject_code, teacher_id))
        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()

def teacher_marked_count(teacher_id, attendance_date):
    conn =get_db_connection()
    cursor =conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(DISTINCT period_no, semester, department) AS marked_count FROM attendance_lock WHERE teacher_id = %s AND attendance_date = %s",
        (teacher_id, attendance_date))
        return cursor.fetchone()['marked_count']

    finally:
        cursor.close()
        conn.close()

def get_teacher_timetable(teacher_id):
    conn =get_db_connection()
    cursor =conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT day ,department , subject_name, period_no, year FROM timetable WHERE teacher_id = %s",
        (teacher_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def get_report(semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM students WHERE semester = %s ORDER BY department",
        (semester,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def take_attendance_report(register_nos, teacher_id):
    if not register_nos:
        return [] 
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        format_strings = ','.join(['%s'] * len(register_nos))
        query = f"""
            SELECT register_no, subject_code, status, name, subject_name, department
            FROM attendance
            WHERE teacher_id = %s AND register_no IN ({format_strings})
        """

        values = [teacher_id]+register_nos
        cursor.execute(query, values)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def get_sem_date_active(department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT * FROM semester_master
            WHERE TRIM(department) = %s
            AND CURDATE() BETWEEN start_date AND end_date
        """
        cursor.execute(query, (department,))
        row = cursor.fetchall()
        if not row:
            return None
        return [r['semester'] for r in row]
    finally:
        cursor.close()
        conn.close()
