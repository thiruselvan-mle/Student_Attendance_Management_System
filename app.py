import os
from flask import Flask, redirect, url_for, render_template
from extensions import cache

try:
    from routes.auth_route import auth
    from routes.teacher_route import teacher
    from routes.incharge_route import incharge
    from routes.hod_route import hod
    from routes.admin_route import admin
    from config import Config
except ImportError as e:
    # Error vantha logs-la clear-ah kaatum
    print(f"Import Error: {e}")
    raise

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config.from_mapping({
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
})
cache.init_app(app)

try:
    app.config.from_object(Config)
except Exception as e:
    print(f"Config Loading Error: {e}")

# 🔴 SAFETY CHECK (IMPORTANT)
if not app.config.get("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY is not set!")

# Registering Blueprints
app.register_blueprint(auth)
app.register_blueprint(teacher)
app.register_blueprint(incharge)
app.register_blueprint(hod)
app.register_blueprint(admin)

@app.route('/')
def home():
    try:
        return redirect(url_for('auth.login'))
    except:
        return redirect('/login') 
    
@app.route("/offline.html")
def offline():
    return render_template("offline.html")

    
if __name__ == "__main__":
    # Railway-oda dynamic port-ah use panna idhu mukkiyam
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    