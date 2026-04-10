from database.db_connection import get_db_connection

def admin_table(admin_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM admin WHERE admin_id=%s", (admin_id,))
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def dept_count():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(DISTINCT department_code) AS department_count FROM department")
        return cursor.fetchone()['department_count']
    
    finally:
        cursor.close()
        conn.close()

def teacher_lis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(DISTINCT teacher_id) AS teacher_count FROM teachers")
        return cursor.fetchone()['teacher_count']
    
    finally:
        cursor.close()
        conn.close()

def student_lis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(DISTINCT register_no) AS student_count FROM students")
        return cursor.fetchone()['student_count']
    
    finally:
        cursor.close()
        conn.close()

def sem_date():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT MIN(start_date) AS start_date, MAX(end_date) AS end_date FROM semester_master WHERE start_date <= CURDATE() AND end_date >= CURDATE() LIMIT 1;""")
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()


def avg_attend(start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT status FROM attendance WHERE attendance_date BETWEEN %s AND %s", (start_date, end_date))
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def get_semester_attendance_by_dept(start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        s.department,
        ROUND(
            (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(a.status), 0)) * 100, 2
        ) AS percentage
    FROM attendance a
    JOIN students s ON a.register_no = s.register_no
    WHERE a.attendance_date BETWEEN %s AND %s
    GROUP BY s.department
    """

    cursor.execute(query, (start_date, end_date))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data

from datetime import date

def get_today_attendance_by_dept(today):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        s.department,
        ROUND(
            (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(a.status), 0)) * 100, 2
        ) AS percentage
    FROM attendance a
    JOIN students s ON a.register_no = s.register_no
    WHERE a.attendance_date = %s
    GROUP BY s.department
    """

    cursor.execute(query, (today,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data

def hod_lis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(" SELECT * FROM hod ")
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def dept_lis():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM department")
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def std_for_each_dept():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""SELECT department AS department, COUNT(*) AS total_students FROM students GROUP BY department"""
        cursor.execute(query)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def chech_dept(department_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""SELECT 1 FROM department WHERE department_code = %s"""
        cursor.execute(query,(department_code,))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

def inst_dept(department_code, department_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""INSERT INTO department(department_code, department_name) VALUES(%s, %s)"""
        cursor.execute(query, (department_code, department_name))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def delt_dept(department_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""DELETE FROM department WHERE department_code = %s"""
        cursor.execute(query, (department_code,))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def check_hod(department,hod_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""SELECT 1 FROM hod WHERE department = %s AND hod_id = %s"""
        cursor.execute(query, (department, hod_id))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()
 
def inst_hod(hod_id, name, email, phone, experience, password, gender, department, start_year, end_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("INSERT INTO hod(hod_id, department, email, name, password, phone, gender, experience, start_year, end_year) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        ,(hod_id, department, email, name, password, phone, gender, experience,start_year, end_year))
        conn.commit()
    
    finally:
        cursor.close()
        conn.close()

def delt_hod(hod_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""DELETE FROM hod WHERE hod_id = %s AND department=%s"""
        cursor.execute(query, (hod_id,department))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def hod_data_for_view(hod_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(" SELECT * FROM hod WHERE hod_id = %s AND department = %s",(hod_id,department))
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def update_hod_for_admin(name, gender, email, phone, experience,start_year, end_year, password, hod_id, department):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE hod SET name=%s, gender=%s, email=%s, phone=%s, experience=%s, password=%s, start_year=%s, end_year=%s
            WHERE hod_id=%s AND department=%s
        """, (name, gender, email, phone, experience, password,start_year,end_year, hod_id, department))

        conn.commit()

    finally:
        cursor.close()
        conn.close()


def incharge_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(" SELECT * FROM incharge ORDER BY department")
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def incharge_data_for_search(search_data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT *
            FROM incharge
            WHERE (incharge_id LIKE %s OR name LIKE %s)
        """
        value = f"%{search_data}%"
        cursor.execute(query, (value, value))
        return cursor.fetchall() 

    finally:
        cursor.close()
        conn.close()

def teacher_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(" SELECT * FROM teachers ORDER BY department")
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def teacher_data_for_search(search_data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT *
            FROM teachers
            WHERE (teacher_id LIKE %s OR name LIKE %s)
        """
        value = f"%{search_data}%"
        cursor.execute(query, (value, value))
        return cursor.fetchall() 

    finally:
        cursor.close()
        conn.close()

def student_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(" SELECT * FROM students ORDER BY department AND register_no")
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def student_data_for_search(search_data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT *
            FROM students
            WHERE (register_no LIKE %s OR name LIKE %s)
        """
        value = f"%{search_data}%"
        cursor.execute(query, (value, value))
        return cursor.fetchall() 

    finally:
        cursor.close()
        conn.close()

def check_students(register_no, phone, email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""SELECT 1 FROM students WHERE (register_no = %s OR email = %s OR phone =%s)"""
        cursor.execute(query, (register_no, email, phone))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

def inst_to_students(register_no, email, name, phone, department, gender, password, year, semester, dob, admission_year, academic_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = f"""INSERT INTO students(register_no, email, name, phone, department, gender, password, year, semester, dob, admission_year, academic_year) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(query, (register_no, email, name, phone, department, gender, password, year, semester, dob, admission_year, academic_year))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def student_data_for_view(register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM students WHERE register_no=%s",(register_no,))
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def student_data_fro_update(register_no, email, name, phone, department, gender, password, dob,
        year, semester, admission_year, academic_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """UPDATE students SET name=%s, email=%s, phone=%s, 
        department=%s, password=%s, gender=%s, dob=%s, year=%s, semester=%s, admission_year=%s, academic_year=%s WHERE register_no = %s"""
        cursor.execute(query, (name, email, phone, department, password, gender, dob,
        year, semester, admission_year, academic_year, register_no))
        conn.commit()

    finally:
        cursor.close()
        conn.close()
        
def delt_student_for_admin(register_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """DELETE FROM students WHERE register_no =%s"""
        cursor.execute(query, (register_no,))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def admin_prf_data(admin_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT * FROM admin WHERE admin_id = %s LIMIT 1""", (admin_id,))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

def promote_std():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                register_no,
                name,
                department,
                academic_year,
                email,
                phone,
                year,
                semester
            FROM students
        """)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
    
def update_std_year_sem(register_no, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE students
            SET year=%s, semester=%s
            WHERE register_no=%s
        """, (year, semester, register_no))
        conn.commit()

    finally:
        cursor.close()
        conn.close()

def get_sem_duration(department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT start_date, end_date
            FROM semester_master
            WHERE department=%s AND year=%s AND semester=%s
        """, (department, year, semester))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def update_sem_duration(department, year, semester, start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE semester_master
            SET start_date=%s, end_date=%s
            WHERE department=%s AND year=%s AND semester=%s
        """, (start_date, end_date, department, year, semester))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def insert_sem_duration(department, year, semester, start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO semester_master
            (department, year, semester, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (department, year, semester, start_date, end_date))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def year_from_sem_master():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(""" SELECT * FROM semester_master
        """)
        return cursor.fetchall()
    
    finally:
        cursor.close()
        conn.close()

def update_sem_mast_year(new_start_date, new_end_date, start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(""" UPDATE semester_master SET start_date = %s, end_date = %s WHERE start_date=%s AND end_date=%s
        """,(new_start_date, new_end_date, start_date, end_date))
        conn.commit()
    
    finally:
        cursor.close()
        conn.close()

def delt_passout_std():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(""" DELETE FROM students WHERE year >=5
        """)
        conn.commit()
    
    finally:
        cursor.close()
        conn.close()

def check_attendance_for_sem():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(""" SELECT 1 FROM attendance LIMIT 1
        """)
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def check_attendance_lock_for_sem():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(""" SELECT 1 FROM attendance_lock LIMIT 1
        """)
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def delt_attned_for_sem():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(""" DELETE FROM attendance
        """)
        conn.commit()
    
    finally:
        cursor.close()
        conn.close()

def delt_attned_lock_for_sem():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(""" DELETE FROM attendance_lock
        """)
        conn.commit()
    
    finally:
        cursor.close()
        conn.close()