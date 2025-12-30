from database.db_connection import get_db_connection

def incharge_table(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM incharge WHERE incharge_id = %s",(user_id,))
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def students_list(class_name, semester, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT register_no, gender FROM students WHERE class_name = %s AND semester = %s AND department =%s ORDER BY register_no",(class_name, semester, department))
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def attendance_list(register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        format_string = ','.join(['%s'] * len(register_no))
        query = f"SELECT register_no, name, status FROM attendance WHERE register_no IN ({format_string})"
        cursor.execute(query,tuple(register_no))
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def load_cls_timetable(class_name, semester, department, day):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM timetable WHERE class_name = %s AND semester = %s AND department =%s AND day = %s",
        (class_name, semester, department, day))
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def update_attendance(register_no, name, subject_name, subject_code, teacher_id, attendance_date, period_no, status, marked_by):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("UPDATE attendance SET status = %s , marked_by =%s WHERE register_no  = %s AND name = %s AND subject_name =%s AND subject_code = %s AND teacher_id = %s AND attendance_date =%s AND period_no=%s",(status, marked_by, register_no, name, subject_name, subject_code, teacher_id, attendance_date, period_no))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def update_attendance_lock(attendance_date, period_no, department, semester, class_name, subject_code, marked_by, role, teacher_id):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("UPDATE attendance_lock SET locked_by = %s , role = %s WHERE attendance_date=%s AND period_no=%s AND department=%s AND semester=%s AND class_name=%s AND subject_code=%s AND teacher_id=%s",
        ( marked_by,  role, attendance_date, period_no, department, semester, class_name, subject_code, teacher_id))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def incharege_timetable(class_name, semester, department):
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM timetable WHERE class_name=%s AND semester=%s AND department=%s",
        (class_name, semester, department ))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def current_month_list(month_start,month_end,register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        format_string = ','.join(['%s'] * len(register_no))
        query = f"SELECT register_no, name, status FROM attendance WHERE attendance_date BETWEEN %s AND %s AND register_no IN ({format_string})"
        values = [month_start,month_end] +register_no
        cursor.execute(query, values)
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()
