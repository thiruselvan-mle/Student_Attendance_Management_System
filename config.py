import secrets

class Config:
    SECRET_KEY = secrets.token_urlsafe(32)

    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = 'thiru@2006'
    DB_NAME = 'student_attendance_management_system'