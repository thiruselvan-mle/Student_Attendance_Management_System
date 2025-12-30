from flask import Flask , Blueprint , redirect , url_for , render_template , request , flash , session
from database.db_connection import get_db_connection

hod = Blueprint('hod', __name__, url_prefix='/hod')

@hod.route('/dashboard', methods = ['GET', 'POST'])
def hod_dashboard():
    return render_template('incharge/dashboard.html')