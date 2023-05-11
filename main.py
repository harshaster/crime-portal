from flask import Flask, render_template, redirect, url_for, flash, request, get_flashed_messages
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import User, Role, db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'

db.init_app(app)

app.app_context().push()

db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

admin_role_id = Role.query.filter_by(name='admin').first().id

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("landing_page.html")

@login_required
@app.route("/dashboard")
def dashboard():
    if current_user.is_authenticated:
        if current_user.role_id == admin_role_id:
            return render_template("admin_dashboard.html")
        else:
            return render_template("user_dashboard.html")

@app.route("/register", methods=["GET", "POST"])
def user_register():
    messages = get_flashed_messages()
    if request.method=="GET":
        return render_template("user_register.html", messages=messages)
    elif request.method=="POST":
        form = request.form
        existing_user = User.query.filter_by(username=form['username']).first()
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('user_register'))

        new_user = User(
            username=form["username"],
            password=form["password"],
            mobile=form["mobile"],
            email=form["email"]
        )
        new_user.role_id=Role.query.filter_by(name='user').first().id
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('user_login'))

@app.route("/login", methods=["GET", "POST"])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method=="POST":
        form = request.form
        user_exists:User = User.query.filter_by(username=form["username"]).first()
        if user_exists:
            if user_exists.check_password(form["password"]):
                login_user(user_exists)
                return redirect(url_for('dashboard'))
            else:
                flash("Username or password incorrect ! ")
        else:
            flash("User does not exist or password incorrect.")
    return render_template("login.html", admin_login=True, messages= get_flashed_messages())
        

@app.route("/admin-login")
def admin_login():
    return render_template("login.html", admin_login=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# User navigation

@app.route("/cfn")
# CFN stands for crime free navigation
def crime_free_navigation():
    return render_template("cfn.html")

@app.route("/sos")
def sos():
    return render_template("sos.html")

@app.route("/report")
def report_crime():
    return render_template("report-crime.html")

@app.route("/grievances")
def grievances():
    return render_template("grievances.html")



# Admin navigation

@app.route("/cctv")
def live_cctv_footage():
    return render_template("CCTV_footage.html")

@app.route("/patrolling-vehicles")
def check_patrolling_vehicles():
    return redirect("/")

@app.route("/crime-reports-at-booth")
def check_crime_reports_at_booth():
    return redirect("/")

@app.route("/crime-rate")
def current_crime_rate_at_location():
    return render_template("crime_rate.html")

@app.route("/closing-crime-report")
def closing_of_a_crime_report():
    return redirect("/")

@app.route("/deploy-patrol")
def deploy_patrolling_vehicle():
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
