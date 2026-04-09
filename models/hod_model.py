from database.db_connection import get_db_connection
from extensions import cache # extensions-ல் இருந்து cache-ஐ இறக்குமதி செய்யவும்

# --- CACHE POTTA FUNCTIONS (Profile & Configuration) ---

@cache.memoize(timeout=600)
def hod_table(hod_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                LOWER(department) AS department,
                LOWER(name) AS name,
                start_year,
                end_year
            FROM hod
            WHERE hod_id = %s
        """, (hod_id,))
        rows = cursor.fetchall()
        departments = list(set(r['department'] for r in rows))
        name = rows[0]['name']
        start_year = min(r['start_year'] for r in rows)
        end_year   = max(r['end_year'] for r in rows)
        return departments, name, start_year, end_year
    finally:
        cursor.close()
        conn.close()

# --- CACHE PODATHA FUNCTIONS (Real-time Counts) ---

def students_count(rows, start_year, end_year):
    # மாணவர் எண்ணிக்கை மாற வாய்ப்புள்ளதால் Cache தேவையில்லை
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholder = ','.join(['%s'] * len(rows))
        query = f"""
            SELECT COUNT(DISTINCT register_no) AS students_count
            FROM students
            WHERE department IN ({placeholder})
            AND year BETWEEN %s AND %s
        """
        cursor.execute(query, tuple(rows) + (start_year, end_year))
        return cursor.fetchone()['students_count']
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=300)
def get_active_semester_for_hod(departments):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholder = ','.join(['%s'] * len(departments))
        query = f"""
            SELECT *
            FROM semester_master
            WHERE department IN ({placeholder})
            AND start_date <= CURDATE()
            AND end_date >= CURDATE()
        """
        cursor.execute(query, departments)
        return cursor.fetchall()  
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=600)
def get_register_nos_by_year(departments, start_year, end_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholders = ','.join(['%s'] * len(departments))
        query = f"""
            SELECT register_no
            FROM students
            WHERE department IN ({placeholders})
            AND year BETWEEN %s AND %s
        """
        cursor.execute(query, tuple(departments) + (start_year, end_year))
        rows = cursor.fetchall()
        return [r['register_no'] for r in rows]
    finally:
        cursor.close()
        conn.close()

# --- ATTENDANCE (Real-time - No Cache) ---

def dept_attendance_percentage(start_date, end_date, register_nos):
    if not register_nos:
        return []
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholders = ','.join(['%s'] * len(register_nos))
        query = f"""
            SELECT status
            FROM attendance
            WHERE attendance_date BETWEEN %s AND %s
            AND register_no IN ({placeholders})
        """
        cursor.execute(query, [start_date, end_date] + register_nos)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=600)
def each_dept_std(department, start_year, end_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholders = ','.join(['%s'] * len(department))
        query = f"""
            SELECT *
            FROM students
            WHERE department IN ({placeholders})
            AND year BETWEEN %s AND %s
            ORDER BY department
        """
        cursor.execute(query, tuple(department) + (start_year, end_year))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# --- TEACHER MANAGEMENT ---

@cache.memoize(timeout=600)
def teacher_lis(start_year, end_year, department=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if department is None:
            query = "SELECT * FROM teachers WHERE teacher_year BETWEEN %s AND %s"
            cursor.execute(query, (start_year, end_year))
        else:
            query = "SELECT * FROM teachers WHERE department = %s AND teacher_year BETWEEN %s AND %s"
            cursor.execute(query, (department, start_year, end_year))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def search_teachers(search_data, start_year, end_year, department=None):
    # தேடுதல் முடிவுகள் எப்போதும் ஃப்ரெஷ்-ஆக இருக்க வேண்டும்
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        value = f"%{search_data}%"
        base_query = """
            SELECT *
            FROM teachers
            WHERE (teacher_id LIKE %s OR name LIKE %s)
              AND teacher_year BETWEEN %s AND %s
        """
        params = [value, value, start_year, end_year]
        if department:
            base_query += " AND department = %s"
            params.append(department)
        cursor.execute(base_query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def check_teachers(teacher_id, email, phone, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT 1 FROM teachers WHERE department = %s AND (teacher_id = %s OR email =%s OR phone =%s) LIMIT 1"
        cursor.execute(query, (department, teacher_id, email, phone))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

def inst_to_teachers(teacher_id, email, name, phone, department, gender, password, experience, teacher_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        INSERT INTO teachers (teacher_id, email, name, phone, department, gender, password, experience, teacher_year) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (teacher_id, email, name, phone, department, gender, password, experience, teacher_year))
        conn.commit()
        cache.delete_memoized(teacher_lis) # புதிய ஆசிரியர் என்பதால் பட்டியலை Clear செய்யவும்
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=600)
def teacher_data_for_edit(teacher_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM teachers WHERE teacher_id = %s AND department =%s"
        cursor.execute(query, (teacher_id, department))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def teacher_data_fro_update(name, email, phone, experience, password, gender, teacher_year, teacher_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """UPDATE teachers SET name=%s, email=%s, phone=%s, 
        experience =%s, password=%s, gender=%s, teacher_year=%s WHERE teacher_id = %s AND department =%s"""
        cursor.execute(query, (name, email, phone, experience, password, gender, teacher_year, teacher_id, department))
        conn.commit()
        cache.delete_memoized(teacher_lis)
        cache.delete_memoized(teacher_data_for_edit, teacher_id, department)
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=300)
def timetable_data_for_teachers(teacher_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM timetable WHERE teacher_id = %s AND department =%s"
        cursor.execute(query, (teacher_id, department))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def delt_teach_for_hod(teacher_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "DELETE FROM teachers WHERE teacher_id = %s AND department =%s"
        cursor.execute(query, (teacher_id, department))
        conn.commit()
        cache.delete_memoized(teacher_lis)
    finally:
        cursor.close()
        conn.close()

# --- INCHARGE MANAGEMENT ---

@cache.memoize(timeout=600)
def incharge_lis(start_year, end_year, department=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if department is None:
            query = "SELECT * FROM incharge WHERE incharge_year BETWEEN %s AND %s"
            cursor.execute(query, (start_year, end_year))
        else:
            query = "SELECT * FROM incharge WHERE department = %s AND incharge_year BETWEEN %s AND %s"
            cursor.execute(query, (department, start_year, end_year))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def search_incharge(search_data, start_year, end_year, department=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        value = f"%{search_data}%"
        base_query = """
            SELECT *
            FROM incharge
            WHERE (incharge_id LIKE %s OR name LIKE %s)
              AND incharge_year BETWEEN %s AND %s
        """
        params = [value, value, start_year, end_year]
        if department:
            base_query += " AND department = %s"
            params.append(department)
        cursor.execute(base_query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def check_incharge(incharge_id, email, phone, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT 1 FROM incharge WHERE department = %s AND (incharge_id = %s OR email =%s OR phone =%s) LIMIT 1"
        cursor.execute(query, (department, incharge_id, email, phone))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

def check_class_assigned(department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT 1 FROM incharge WHERE department = %s AND year = %s AND semester = %s LIMIT 1"
        cursor.execute(query, (department, year, semester))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

def inst_to_incharge(incharge_id, email, name, phone, department, gender, password, experience, year, semester, incharge_year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        INSERT INTO incharge (incharge_id, email, name, phone, department, gender, password, experience, year, semester, incharge_year) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (incharge_id, email, name, phone, department, gender, password, experience, year, semester, incharge_year))
        conn.commit()
        cache.delete_memoized(incharge_lis)
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=600)
def incharge_data_for_edit(incharge_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM incharge WHERE incharge_id = %s AND department =%s"
        cursor.execute(query, (incharge_id, department))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def chech_update_data_incharge(year, semester, department, incharge_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT 1 FROM incharge WHERE year=%s AND semester=%s AND department=%s AND incharge_id != %s"
        cursor.execute(query, (year, semester, department, incharge_id))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def incharge_data_fro_update(name, email, phone, experience, password, gender, incharge_year, year, semester, incharge_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """UPDATE incharge SET name=%s, email=%s, phone=%s, 
        experience =%s, password=%s, gender=%s, incharge_year=%s, year=%s, semester=%s WHERE incharge_id = %s AND department =%s"""
        cursor.execute(query, (name, email, phone, experience, password, gender, incharge_year, year, semester, incharge_id, department))
        conn.commit()
        cache.delete_memoized(incharge_lis)
        cache.delete_memoized(incharge_data_for_edit, incharge_id, department)
    finally:
        cursor.close()
        conn.close()
        
def delt_incharge_for_hod(incharge_id, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "DELETE FROM incharge WHERE incharge_id = %s AND department =%s"
        cursor.execute(query, (incharge_id, department))
        conn.commit()
        cache.delete_memoized(incharge_lis)
    finally:
        cursor.close()
        conn.close()

# --- STUDENT & SEMESTER HELPERS ---

def each_year_std(department, year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM students WHERE year = %s AND department =%s"
        cursor.execute(query, (year, department))
        std = cursor.fetchall()
        sem = [s['semester'] for s in std]
        reg_no = [s['register_no'] for s in std]
        return std, sem[0], reg_no
    finally:
        cursor.close()
        conn.close()

def active_sem_for_year(departments, year, today):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try: 
        query = "SELECT * FROM semester_master WHERE department = %s AND year =%s AND start_date <= %s AND end_date >= %s"
        cursor.execute(query, (departments, year, today, today))
        return cursor.fetchone()  
    finally:
        cursor.close()
        conn.close()
        
def year_attendance(start_date, end_date, reg_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholders = ','.join(['%s'] * len(reg_no))
        query = f"SELECT status, register_no, name FROM attendance WHERE attendance_date BETWEEN %s AND %s AND register_no IN ({placeholders})"
        values = [start_date, end_date] + reg_no
        cursor.execute(query, values)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=300)
def teacher_subject_map(semester, year, department):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try: 
        query = "SELECT subject_name, subject_code, teacher_id FROM subjects WHERE department = %s AND year =%s AND semester = %s"
        cursor.execute(query, (department, year, semester))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# --- TIMETABLE & SUBJECT ASSIGNMENT (Critical - No Cache on Writes) ---

def insert_timetable(day, department, period_no, semester, subject_code, teacher_id, year, start_time, end_time):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try: 
        query = """
                INSERT INTO timetable
                (day, department, period_no,
                semester, subject_code, subject_name,
                teacher_id, year, start_time, end_time)
                VALUES (%s,%s,%s,%s,%s,(SELECT subject_name FROM subjects WHERE subject_code=%s LIMIT 1),%s,%s,%s,%s)
                """
        cursor.execute(query, (day, department, period_no, semester, subject_code, subject_code, teacher_id, year, start_time, end_time))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=300)
def fetch_timetable(department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT day, period_no, subject_code, teacher_id FROM timetable WHERE department=%s AND year=%s AND semester=%s", (department, year, semester))
        data = {}
        for r in cursor.fetchall():
            data.setdefault(r['day'], {})[r['period_no']] = f"{r['subject_code']}|{r['teacher_id']}"
        return data
    finally:
        cursor.close()
        conn.close()

def delete_existing_timetable(department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM timetable WHERE department=%s AND year=%s AND semester=%s", (department, year, semester))
        conn.commit()
        cache.delete_memoized(fetch_timetable, department, year, semester)
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=600)
def all_teachers_lis_for_sub():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT teacher_id, name FROM teachers ORDER BY department")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=300)
def fetch_assigned_subjects(department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT subject_code, subject_name, teacher_id FROM subjects WHERE department = %s AND year = %s AND semester = %s ORDER BY subject_code"
        cursor.execute(query, (department, year, semester))
        rows = cursor.fetchall()
        return [{"code": r["subject_code"], "name": r["subject_name"], "teacher_id": r["teacher_id"]} for r in rows]
    finally:
        cursor.close()
        conn.close()

def delete_existing_subjects(department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM subjects WHERE department=%s AND year=%s AND semester=%s", (department, year, semester))
        conn.commit()
        cache.delete_memoized(fetch_assigned_subjects, department, year, semester)
    finally:
        cursor.close()
        conn.close()

def insert_subject_assign(subject_code, subject_name,teacher_id, department, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO subjects (subject_code, subject_name, teacher_id, department, year, semester) VALUES (%s,%s,%s,%s,%s,%s)", (subject_code,subject_name,teacher_id,department,year,semester))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

@cache.memoize(timeout=600)
def hod_prf_data(hod_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM hod WHERE hod_id = %s LIMIT 1", (hod_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()