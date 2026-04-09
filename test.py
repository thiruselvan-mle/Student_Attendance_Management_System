import os
import mysql.connector

try:
    conn = mysql.connector.connect(
            # Using the external proxy host and port from your dashboard image
            host=os.getenv("MYSQLHOST", "mainline.proxy.rlwy.net"),
            user=os.getenv("MYSQLUSER", "root"),
            password=os.getenv("MYSQLPASSWORD", "RlZHCZODSwjoBzETSCeVAWQMrtYJWPiV"),
            database=os.getenv("MYSQLDATABASE", "railway"),
            port=int(os.getenv("MYSQLPORT", 57245)) 
        )

except mysql.connector.Error as err:
    print(f"Database Connection Error: {err}")
    
cursor = conn.cursor()

# STUDENTS
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS students (
#     register_no      VARCHAR(50)  NOT NULL,
#     name             VARCHAR(100) NOT NULL,
#     department       VARCHAR(70)  NOT NULL,
#     year             INT          NOT NULL,
#     semester         INT          NOT NULL DEFAULT 1,
#     phone            VARCHAR(15)  NOT NULL,
#     gender           VARCHAR(10)  NOT NULL,
#     dob              DATE         NOT NULL,
#     admission_year   INT          NOT NULL,
#     email            VARCHAR(255) NOT NULL,
#     password         VARCHAR(255) NOT NULL,
#     academic_year    VARCHAR(60)  NOT NULL,

#     PRIMARY KEY (register_no),
#     INDEX idx_department (department),
#     INDEX idx_year_sem (year, semester)
# );
# """)

# # # TEACHERS
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS teachers (
#     teacher_id   VARCHAR(50)  NOT NULL,
#     department   VARCHAR(70)  NOT NULL,
#     name         VARCHAR(100) NOT NULL,
#     phone        VARCHAR(15),
#     email        VARCHAR(100),
#     gender       VARCHAR(10),
#     password     VARCHAR(255) NOT NULL,
#     experience   INT          NOT NULL DEFAULT 3,

#     PRIMARY KEY (teacher_id, department),
#     INDEX idx_teacher_id (teacher_id),
#     INDEX idx_teacher_department (department)
# );
# """)

# # # INCHARGE
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS incharge (
#     incharge_id   VARCHAR(50)  NOT NULL,
#     department    VARCHAR(100) NOT NULL,
#     name          VARCHAR(100) NOT NULL,
#     year          INT          NOT NULL,
#     semester      INT          NOT NULL,
#     phone         VARCHAR(15)  NOT NULL,
#     email         VARCHAR(100) NOT NULL,
#     password      VARCHAR(255) NOT NULL,
#     experience    INT          NOT NULL,
#     gender        VARCHAR(10)  NOT NULL,

#     PRIMARY KEY (incharge_id, department),
#     INDEX idx_incharge_dept_year_sem (department, year, semester),
#     INDEX idx_incharge_id (incharge_id)
# );
# """)

# # HOD
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS hod (
#     hod_id VARCHAR(50) NOT NULL,
#     department VARCHAR(100) NOT NULL,
#     name VARCHAR(100) NOT NULL,
#     email VARCHAR(100) NOT NULL,
#     phone VARCHAR(15) NOT NULL,
#     password VARCHAR(255) NOT NULL,
#     gender VARCHAR(10) NOT NULL,
#     experience INT NOT NULL DEFAULT 3,

#     PRIMARY KEY (hod_id, department),
#     INDEX idx_hod_department (department),
#     INDEX idx_hod_id (hod_id)
# );
# """)

# # ADMIN  (idx_admin_id REMOVED)
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS admin (
#     admin_id VARCHAR(50) NOT NULL,
#     name VARCHAR(100) NOT NULL,
#     phone VARCHAR(15) NOT NULL,
#     email VARCHAR(100) NOT NULL,
#     password VARCHAR(255) NOT NULL,

#     PRIMARY KEY (admin_id)
# );
# """)

# # ATTENDANCE
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS attendance (
#     register_no VARCHAR(50) NOT NULL,
#     attendance_date DATE NOT NULL,
#     period_no INT NOT NULL,
#     subject_code VARCHAR(100) NOT NULL,
#     subject_name VARCHAR(100) NOT NULL,
#     teacher_id VARCHAR(50) NOT NULL,
#     marked_by VARCHAR(50) NOT NULL,
#     name VARCHAR(100) NOT NULL,
#     department VARCHAR(100) NOT NULL,
#     status ENUM('Present','Absent') NOT NULL DEFAULT 'Present',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

#     PRIMARY KEY (register_no, attendance_date, period_no),
#     INDEX idx_attendance_register_no (register_no),
#     INDEX idx_attendance_teacher_id (teacher_id),
#     INDEX idx_attendance_department (department),
#     INDEX idx_attendance_date (attendance_date),
#     INDEX idx_attendance_status (status)
# );
# """)

# # ATTENDANCE LOCK
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS attendance_lock (
#     attendance_date DATE NOT NULL,
#     period_no INT NOT NULL,
#     department VARCHAR(100) NOT NULL,
#     semester INT NOT NULL,
#     subject_code VARCHAR(100) NOT NULL,
#     locked_by VARCHAR(50) NOT NULL,
#     role ENUM('teacher','incharge','hod') NOT NULL,
#     teacher_id VARCHAR(50) NOT NULL,
#     locked_at DATETIME DEFAULT CURRENT_TIMESTAMP,

#     PRIMARY KEY (
#         attendance_date,
#         period_no,
#         department,
#         semester,
#         subject_code
#     ),
#     INDEX idx_lock_department (department),
#     INDEX idx_lock_semester (semester),
#     INDEX idx_lock_date (attendance_date),
#     INDEX idx_lock_attendance_data_period_no (attendance_date, period_no)
# );
# """)

# # TIMETABLE

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS timetable (
#     department VARCHAR(100) NOT NULL,
#     year INT NOT NULL,
#     semester INT NOT NULL,
#     day ENUM(
#         'Monday','Tuesday','Wednesday',
#         'Thursday','Friday','Saturday'
#     ) NOT NULL,
#     period_no INT NOT NULL,
#     start_time TIME NOT NULL,
#     end_time TIME NOT NULL,
#     subject_code VARCHAR(100) NOT NULL,
#     subject_name VARCHAR(100) NOT NULL,
#     teacher_id VARCHAR(50) NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

#     PRIMARY KEY (department, year, semester, day, period_no),
#     INDEX idx_tt_teacher (teacher_id),
#     INDEX idx_tt_subject (subject_code),
#     INDEX idx_tt_day (day),
#     INDEX idx_tt_department (department),
#     INDEX idx_tt_year_sem (year, semester)
# );
# """)

# # SUBJECTS
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS subjects (
#     subject_code VARCHAR(100) NOT NULL,
#     subject_name VARCHAR(100) NOT NULL,
#     department VARCHAR(100) NOT NULL,
#     year INT NOT NULL,
#     semester INT DEFAULT 1,
#     teacher_id VARCHAR(50),

#     PRIMARY KEY (subject_code, department, year, semester),
#     INDEX idx_sub_department (department),
#     INDEX idx_sub_year (year),
#     INDEX idx_sub_semester (semester),
#     INDEX idx_sub_teacher (teacher_id),
#     INDEX idx_sub_dept_year_sem (department, year, semester)
# );
# """)

# # SEMESTER MASTER
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS semester_master (
#     department VARCHAR(100) NOT NULL,
#     year INT NOT NULL,
#     semester INT NOT NULL,
#     start_date DATE NOT NULL,
#     end_date DATE NOT NULL,

#     PRIMARY KEY (department, year, semester),
#     INDEX idx_sm_department (department),
#     INDEX idx_sm_year (year),
#     INDEX idx_sm_semester (semester)
# );
# """)

# # DEPARTMENT
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS department (
#     department_code VARCHAR(100) NOT NULL,
#     department_name VARCHAR(100) NOT NULL,

#     PRIMARY KEY (department_code),
#     INDEX idx_dept_name (department_name)
# );
# """)

# cursor.execute("""insert into admin (admin_id, name, phone, email, password) values ('ad001', 'Admin User', '1234567890', 'admin@example.com', 'password123')""")


# conn.commit()
# cursor.close()
# conn.close()
