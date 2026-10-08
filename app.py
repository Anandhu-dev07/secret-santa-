"""
Flask Application for Secret Santa - Horror Edition.
Features secure session authentication, RESTful APIs, horror error handling,
and transactional Secret Santa assignment logic.
"""

import os
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# Configure secure session cookies
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=86400  # 24 hours
)

# Initialize database on startup if not already seeded
with app.app_context():
    db.init_db()
    if db.get_all_users_count() == 0:
        db.seed_sample_students()

def login_required(f):
    """Decorator ensuring student is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "YOUR PRESENCE HAS DISAPPEARED. PLEASE LOG IN."}), 401
            return redirect(url_for("index", msg="unauthorized"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    """Horror Landing and Authentication Portal."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    """Handles student authentication securely."""
    data = request.form if request.form else (request.get_json() or {})
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        msg = "THE DOOR REMAINS LOCKED. Credentials are incomplete."
        if request.is_json:
            return jsonify({"success": False, "error": msg}), 400
        return render_template("index.html", error=msg)

    user = db.authenticate_user(email, password)
    if not user:
        msg = "THE DOOR REMAINS LOCKED. Invalid soul credentials."
        if request.is_json:
            return jsonify({"success": False, "error": msg}), 401
        return render_template("index.html", error=msg)

    # Establish session
    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    session.permanent = True

    if request.is_json:
        return jsonify({"success": True, "redirect": url_for("dashboard")})
    return redirect(url_for("dashboard"))

@app.route("/register", methods=["POST"])
def register():
    """Handles new student registration."""
    data = request.form if request.form else (request.get_json() or {})
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    preference = data.get("preference", "").strip()

    if not name or not email or not password or not preference:
        msg = "ALL PORTALS MUST BE FILLED TO SUMMON YOUR PRESENCE."
        if request.is_json:
            return jsonify({"success": False, "error": msg}), 400
        return render_template("index.html", reg_error=msg)

    if "@" not in email:
        msg = "AN UNKNOWN GMAIL ESSENCE WAS PROVIDED."
        if request.is_json:
            return jsonify({"success": False, "error": msg}), 400
        return render_template("index.html", reg_error=msg)

    user_id, err = db.create_user(name, email, password, preference)
    if err:
        if request.is_json:
            return jsonify({"success": False, "error": err}), 400
        return render_template("index.html", reg_error=err)

    # Log in newly registered student
    session.clear()
    session["user_id"] = user_id
    session["user_name"] = name
    session["user_email"] = email
    session.permanent = True

    if request.is_json:
        return jsonify({"success": True, "redirect": url_for("dashboard")})
    return redirect(url_for("dashboard"))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Clears the session and banishes user."""
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Horror Gothic Mansion Dashboard."""
    user = db.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("index"))

    has_played, played_time = db.check_participation(user["id"])
    total_souls = db.get_all_users_count()

    return render_template(
        "dashboard.html",
        user=user,
        has_played=has_played,
        played_time=played_time,
        total_souls=total_souls
    )

@app.route("/secret-santa")
@login_required
def secret_santa():
    """Secret Santa Selection Chamber with 25-Color Wheel and Dart throw."""
    user = db.get_user_by_id(session["user_id"])
    has_played, played_time = db.check_participation(user["id"])

    return render_template(
        "secret_santa.html",
        user=user,
        has_played=has_played,
        played_time=played_time
    )

@app.route("/result")
@login_required
def result():
    """Displays the revealed secret friend and gift wish once unlocked."""
    user_id = session["user_id"]
    has_played, _ = db.check_participation(user_id)

    if not has_played:
        # Cannot view result before completing the ritual
        return redirect(url_for("secret_santa"))

    recipient = db.get_assigned_recipient(user_id)
    if not recipient:
        return render_template("result.html", error="THE WHEEL HAS NOT YET BEEN CAST.")

    return render_template("result.html", recipient=recipient)

# --- Horror JSON APIs ---

@app.route("/api/wheel-data", methods=["GET"])
@login_required
def get_wheel_data():
    """
    Returns the visual layout of the 25-color wheel.
    Privacy guarantee: Only returns disguised aliases and colors.
    Does NOT reveal which student belongs to which slice!
    """
    user_id = session["user_id"]
    has_played, _ = db.check_participation(user_id)

    slices, _ = db.get_wheel_layout_for_user(user_id)
    return jsonify({
        "success": True,
        "slices": slices,
        "has_played": has_played,
        "total_slices": len(slices)
    })

@app.route("/api/throw-dart", methods=["POST"])
@login_required
def throw_dart():
    """
    Handles the dart throw action.
    Validates participation and server-side assigns target slice for animation.
    Enforces strict single-attempt rule.
    """
    user_id = session["user_id"]
    has_played, played_time = db.check_participation(user_id)

    if has_played:
        return jsonify({
            "success": False,
            "error": "THAT WAS YOUR LAST CHANCE. NO MORE CHANCES REMAIN.",
            "code": "ALREADY_PLAYED"
        }), 403

    slices, target_slice_index = db.get_wheel_layout_for_user(user_id)
    if target_slice_index == -1:
        # Fallback safeguard in case assignments were reset
        return jsonify({
            "success": False,
            "error": "THE SPIRITS ARE RESTLESS. TRY AGAIN."
        }), 500

    # Calculate stop angle for the target slice
    # 25 slices = 360 / 25 = 14.4 degrees per slice
    slice_deg = 360.0 / 25.0
    # Pointer is at top (270 or 0 deg). Landing at target slice:
    # Wheel rotates clockwise by full spins + target slice offset
    target_angle = (360.0 - (target_slice_index * slice_deg + (slice_deg / 2.0))) % 360.0

    return jsonify({
        "success": True,
        "target_slice_index": target_slice_index,
        "slice_name": slices[target_slice_index]["disguised_name"],
        "target_angle": target_angle,
        "slice_deg": slice_deg
    })

@app.route("/api/reveal", methods=["POST"])
@login_required
def reveal():
    """
    Horror 'OPEN IT' reveal action.
    Marks participation complete and returns the actual secret friend recipient.
    """
    user_id = session["user_id"]
    data = request.get_json() or {}
    slice_index = data.get("slice_index", None)

    has_played, _ = db.check_participation(user_id)
    if has_played:
        # Fetch existing recipient
        recipient = db.get_assigned_recipient(user_id)
        return jsonify({
            "success": True,
            "already_revealed": True,
            "recipient_name": recipient["name"],
            "gift_preference": recipient["gift_preference"]
        })

    # Complete participation in atomic transaction
    db.mark_participation_complete(user_id, wheel_slice_index=slice_index)
    recipient = db.get_assigned_recipient(user_id)

    if not recipient:
        return jsonify({"success": False, "error": "THE SPIRITS ARE RESTLESS. TRY AGAIN."}), 500

    return jsonify({
        "success": True,
        "already_revealed": False,
        "recipient_name": recipient["name"],
        "gift_preference": recipient["gift_preference"]
    })

@app.route("/api/status", methods=["GET"])
def api_status():
    """Returns current user status and realm statistics."""
    if "user_id" not in session:
        return jsonify({"authenticated": False})
    
    user = db.get_user_by_id(session["user_id"])
    has_played, played_time = db.check_participation(session["user_id"])
    return jsonify({
        "authenticated": True,
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "has_played": has_played,
        "played_time": str(played_time) if played_time else None
    })

# --- Error Handlers ---

@app.errorhandler(404)
def error_404(e):
    return render_template("index.html", error="THE DOOR REMAINS LOCKED. THIS REALM DOES NOT EXIST."), 404

@app.errorhandler(403)
def error_403(e):
    return render_template("index.html", error="YOU ARE NOT MEANT TO SEE THIS."), 403

@app.errorhandler(500)
def error_500(e):
    return render_template("index.html", error="THE SPIRITS ARE RESTLESS. TRY AGAIN."), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
