from flask import Flask
from routes.auth_route import auth
from routes.student_route import student
from routes.teacher_route import teacher
from routes.incharge_route import incharge
from routes.hod_route import hod
from routes.admin_route import admin
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth)
app.register_blueprint(student)
app.register_blueprint(teacher)
app.register_blueprint(incharge)
app.register_blueprint(hod)
app.register_blueprint(admin)

if __name__ == "__main__":
    app.run(debug=True)
