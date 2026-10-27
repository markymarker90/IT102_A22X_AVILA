# LabPulse: Computer Laboratory Utilization and Fault Tracking System

LabPulse is a full-stack Python web application designed to manage computer laboratory sessions, track workstation utilization, and handle hardware/software fault reporting. It is built with Object-Oriented Programming (OOP) principles, utilizing a polymorphic role-based access system for Students, Instructors, and Lab Custodians.

## 🚀 Key Features

* **Role-Based Authentication:** Secure login and registration system with tailored dashboard privileges for `Student`, `Instructor`, and `LabCustodian` classes using OOP polymorphism.
* **Workstation Tracking:** Real-time check-in and check-out system for laboratory PCs, preventing overlapping sessions and tracking pre-session conditions.
* **Fault Ticketing System:** Users can report hardware, software, or network issues. Tickets are dynamically categorized by severity (Low, High, Critical), with Critical faults automatically locking the affected workstation.
* **Automated Log Exporting:** Instructors and Custodians can generate and export complete system utilization logs and maintenance records directly to CSV files.
* **Embedded Database:** Powered by a lightweight, zero-configuration SQLite3 database (`labpulse.db`) handled natively through Python.

## 🛠️ Technology Stack

* **Backend:** Python 3, Flask (Web Framework)
* **Frontend:** HTML5, CSS3, Jinja2 Templating
* **Database:** SQLite3 (Built-in Python `sqlite3` library)
* **Environment:** GitHub Codespaces / Python Virtual Environment

## 📁 Project Structure

```text
labpulse/
├── templates/
│   ├── login.html       # User authentication and registration views
│   ├── register.html    # Account creation interface
│   └── dashboard.html   # Main application interface and workstation map
├── static/
│   └── style.css        # Application styling and UI layout
├── exports/             # Directory for generated CSV utilization and fault logs
├── main.py              # Flask server routing and session management
├── controller.py        # Core application logic and database interactions
├── models.py            # OOP class definitions (Users, Workstations, Tickets)
└── labpulse.db          # Auto-generated SQLite database