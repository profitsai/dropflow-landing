import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_mail import Mail, Message
from flask_migrate import Migrate
from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db


load_dotenv()


def _env_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:///dropflow.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = _env_bool(os.getenv("MAIL_USE_TLS"), default=True)
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_DEFAULT_SENDER", app.config.get("MAIL_USERNAME") or "no-reply@dropflow.local"
)


db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
migrate = Migrate(app, db)
mail = Mail(app)


RESET_PASSWORD_SALT = "reset-password"
RESET_PASSWORD_TOKEN_MAX_AGE_SECONDS = 3600


def _password_reset_serializer():
    return URLSafeTimedSerializer(app.config["SECRET_KEY"])


def generate_password_reset_token(email):
    serializer = _password_reset_serializer()
    return serializer.dumps(email, salt=RESET_PASSWORD_SALT)


def verify_password_reset_token(token, max_age=RESET_PASSWORD_TOKEN_MAX_AGE_SECONDS):
    serializer = _password_reset_serializer()
    try:
        email = serializer.loads(token, salt=RESET_PASSWORD_SALT, max_age=max_age)
    except (BadSignature, BadTimeSignature):
        return None

    if not email:
        return None

    return User.query.filter_by(email=email).first()


def send_transactional_email(to_email, subject, template_name, **kwargs):
    html_body = render_template(f"emails/{template_name}", **kwargs)

    if not app.config.get("MAIL_PASSWORD"):
        print("\n" + "=" * 80)
        print("[MOCK EMAIL] MAIL_PASSWORD not configured — email not sent")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Template: emails/{template_name}")
        print("-" * 80)
        print(html_body)
        print("=" * 80 + "\n")
        return False

    msg = Message(subject=subject, recipients=[to_email], html=html_body)
    mail.send(msg)
    return True


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/terms")
def terms():
    return render_template("public/legal.html", page_title="Terms of Service")


@app.route("/privacy")
def privacy():
    return render_template("public/legal.html", page_title="Privacy Policy")


@app.route("/refund")
def refund():
    return render_template("public/legal.html", page_title="Refund Policy")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()

        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                reset_token = generate_password_reset_token(user.email)
                reset_url = url_for(
                    "reset_password_token", token=reset_token, _external=True
                )
                send_transactional_email(
                    to_email=user.email,
                    subject="Reset your DropFlow password",
                    template_name="reset_password.html",
                    reset_url=reset_url,
                )

        # Keep response the same whether user exists or not (no account enumeration)
        return render_template("auth/forgot_password.html", submitted=True)

    return render_template("auth/forgot_password.html", submitted=False)


@app.route("/reset-password")
def reset_password():
    return redirect(url_for("forgot_password"))


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    user = verify_password_reset_token(token)
    if not user:
        return render_template(
            "auth/reset_password.html", token=token, token_valid=False, error="This password reset link is invalid or has expired."
        )

    if request.method == "POST":
        password = request.form.get("password") or ""

        if not password:
            return render_template(
                "auth/reset_password.html",
                token=token,
                token_valid=True,
                error="Please enter a new password.",
            )

        user.password_hash = generate_password_hash(password)
        db.session.commit()
        flash("Your password has been reset. Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("auth/reset_password.html", token=token, token_valid=True)


@app.route("/signup", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            return render_template("signup.html", error="Email and password are required.")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template("signup.html", error="An account with that email already exists.")

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=(request.form.get("name") or "").strip() or None,
        )
        db.session.add(user)
        db.session.commit()

        login_url = url_for("login", _external=True)
        send_transactional_email(
            to_email=user.email,
            subject="Welcome to DropFlow",
            template_name="welcome.html",
            login_url=login_url,
        )

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("app/dashboard.html")


@app.route("/products")
@login_required
def products():
    return render_template("app/inventory.html")


@app.route("/products/<product_id>")
@login_required
def product_single(product_id):
    # Pass the ID to the template so we can use it dynamically later
    return render_template("app/product_detail.html", product_id=product_id)


@app.route("/orders")
@login_required
def orders():
    return render_template("app/order_history.html")


@app.route("/orders/<order_id>")
@login_required
def order_single(order_id):
    # Pass the ID to the template for dynamic rendering
    return render_template("app/order_detail.html", order_id=order_id)


@app.route("/import")
@login_required
def import_page():
    return render_template("import.html")


@app.route("/scraper")
@login_required
def scraper():
    return render_template("app/scraper.html")


@app.route("/settings")
@login_required
def settings():
    return render_template("app/settings.html")


@app.route("/upgrade-success")
@login_required
def upgrade_success():
    # In a real app, you'd verify the Stripe session ID here first
    return render_template("app/upgrade_success.html")


@app.route("/upgrade-cancelled")
@login_required
def upgrade_cancelled():
    return render_template("app/upgrade_cancelled.html")


if __name__ == "__main__":
    app.run(debug=True)
