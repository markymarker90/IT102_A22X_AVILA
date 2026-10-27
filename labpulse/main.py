import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from controller import LabPulseController


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "labpulse-dev-secret-key-2026")

controller = LabPulseController()


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return controller.get_user_by_id(user_id)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "").strip()

        user = controller.authenticate_user(user_id, password)
        if user:
            session["user_id"] = user.get_user_id()
            flash(f"Welcome, {user.get_full_name()} ({user.get_role()})!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Student/Staff ID or Password/PIN.", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_id = request.form.get("user_id", "")
        full_name = request.form.get("full_name", "")
        password = request.form.get("password", "")
        role = request.form.get("role", "Student")
        meta_info = request.form.get("meta_info", "")

        try:
            msg = controller.register_user(user_id, full_name, password, role, meta_info)
            flash(msg, "success")
            return redirect(url_for("login"))
        except Exception as exc:
            flash(str(exc), "error")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    selected_pc = request.args.get("pc", "PC-01")
    dashboard_config = user.loadDashboard()  # Polymorphic method call

    return render_template(
        "dashboard.html",
        user=user,
        config=dashboard_config,
        workstations=controller.get_all_workstations(),
        selected_ws=controller.get_workstation(selected_pc),
        sessions=controller.get_recent_sessions(),
        tickets=controller.get_fault_tickets()
    )


@app.route("/action", methods=["POST"])
def handle_action():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    action_type = request.form.get("action_type")
    pc_id = request.form.get("pc_id", "PC-01")

    payload = {
        "pc_id": pc_id,
        "pre_condition": request.form.get("pre_condition", "All Hardware & Software OK"),
        "category": request.form.get("category", "Hardware"),
        "severity": request.form.get("severity", "Low"),
        "description": request.form.get("description", ""),
        "ticket_id": int(request.form.get("ticket_id", 0)) if request.form.get("ticket_id", "").isdigit() else 0
    }

    try:
        # Polymorphic execution based on Student, Instructor, or LabCustodian role
        result_msg = user.processAction(controller, action_type, payload)
        flash(result_msg, "success")
    except Exception as exc:
        flash(str(exc), "error")

    return redirect(url_for("dashboard", pc=pc_id))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)