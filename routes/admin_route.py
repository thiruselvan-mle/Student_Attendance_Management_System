from flask import Flask , Blueprint , redirect , url_for , render_template , request , flash , session
from database.db_connection import get_db_connection

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard', methods = ['GET', 'POST'])
def admin_dashboard():
    return render_template('incharge/dashboard.html')