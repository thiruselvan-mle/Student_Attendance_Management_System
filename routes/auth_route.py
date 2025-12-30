from flask import Blueprint, render_template, request, redirect, url_for, session , flash

from models.auth_model import user_authentication
from models.auth_model import forget_password

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        user_id = request.form['user_id']
        password = request.form['password']

        if role == 'student':  
            student = user_authentication(table="students", id="register_no", user_id =user_id, password=password)

            if student:
                session['register_no'] = student['register_no']
                session['role'] = role
                return redirect(url_for('student.student_dashboard'))
            else:
                flash('Invalid Register No Or Password!', 'danger')

        elif role == 'teacher':
            teacher = user_authentication(table='teachers', id='teacher_id', user_id=user_id, password=password)

            if teacher:
                session['teacher_id'] = teacher['teacher_id']
                session['role'] = role
                return redirect(url_for('teacher.teacher_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')

        elif role == 'incharge':
            incharge = user_authentication(table='incharge', id ='incharge_id', user_id=user_id, password=password)

            if incharge:
                session['incharge_id'] = incharge['incharge_id']
                session['role'] = role
                return redirect(url_for('incharge.incharge_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')
           
        elif role == 'hod':
            hod = user_authentication(table='hod', id='hod_id', user_id=user_id, password=password)

            if hod:
                session['hod_id'] = hod['hod_id']
                session['role'] = role
                return redirect(url_for('hod.hod_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')
            
        elif role == 'admin':
            admin = user_authentication(table='admin', id='admin_id', user_id=user_id, password=password)

            if admin:
                session['admin_id'] = admin['admin_id']
                session['role'] = role
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid ID Or Password!', 'danger')

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash("Successfully logout", "success")
    return redirect(url_for('auth.login'))

@auth.route('/forget', methods = ['POST', 'GET'])
def forget():
    if request.method == 'POST':
        user_id = request.form['user_id']
        new_password = request.form['new_password']

        success = forget_password(user_id, new_password)
        if success:
            flash("Password reset successfully", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Invalid User_id", "danger")
     
    return render_template('auth/forget.html')