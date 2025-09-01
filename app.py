from flask import Flask, request, redirect, session, render_template, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from dotenv import load_dotenv
import urllib.parse

# load env first
load_dotenv()

# safely quote password (handle special chars)
db_pass = urllib.parse.quote_plus(os.getenv("DB_PASS", ""))

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv("FLASK_SECRET", "dev_secret")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{db_pass}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Models ---
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("user", "admin"), default="user")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    feeds = db.relationship("Feed", backref="user", cascade="all, delete")


class Feed(db.Model):
    __tablename__ = "feeds"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    feed_name = db.Column(db.String(200))
    feed_code = db.Column(db.String(100))
    report_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(12, 2))
    data = db.Column(db.JSON)


# --- Helper decorator ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


# --- Routes ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm_password', '')

    if not (username and email and password and confirm):
        return "Please provide username, email and password", 400

    if password != confirm:
        return "Passwords do not match", 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return "Username or email already exists", 409

    pw_hash = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=pw_hash, role="user")
    db.session.add(user)
    db.session.commit()

    return redirect('/')


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user or not check_password_hash(user.password_hash, password):
        return "Invalid credentials", 401

    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

    return redirect(url_for("dashboard"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    feeds = Feed.query.filter_by(user_id=user.id).order_by(Feed.report_date.desc()).limit(20).all()
    return render_template("dashboard.html", user=user, feeds=feeds, role=user.role)


@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    users = User.query.order_by(User.id.desc()).limit(100).all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/feedeyes')
@login_required
def feedeyes():
    # Render the Feedeyes UI (templates/feedeyes.html)
    return render_template('feedeyes.html')

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    # Example: fetch the report by id and show it
    rpt = Feed.query.get(report_id)
    if not rpt or rpt.user_id != session.get('user_id') and session.get('role') != 'admin':
        return "Not found or unauthorized", 404
    # You can create `templates/report.html` to show full details.
    return render_template('report.html', report=rpt)

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    
    user = User.query.get(user_id)  # if using SQLAlchemy
    return render_template("profile.html", user=user)


from datetime import date

@app.route("/report/new", methods=["GET", "POST"])
@login_required
def new_report():
    if request.method == "POST":
        feed_name = request.form.get("feed_name")
        feed_code = request.form.get("feed_code")
        amount = request.form.get("amount")

        rpt = Feed(
            user_id=session["user_id"],
            feed_name=feed_name,
            feed_code=feed_code,
            report_date=date.today(),
            amount=amount or 0,
            data={}  # you can later store JSON with full formulation
        )
        db.session.add(rpt)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("new_report.html")


@app.route("/reports")
@login_required
def reports():
    user = User.query.get(session["user_id"])
    if session.get("role") == "admin":
        # Admin sees all reports
        feeds = Feed.query.order_by(Feed.report_date.desc()).all()
    else:
        # User sees only their own reports
        feeds = Feed.query.filter_by(user_id=user.id).order_by(Feed.report_date.desc()).all()

    return render_template("reports.html", feeds=feeds, user=user)



if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
