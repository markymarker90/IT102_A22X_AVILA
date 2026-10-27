import os
import csv
import hashlib
import sqlite3
from datetime import datetime
from models import (
    User, Student, Instructor, LabCustodian,
    Workstation, SessionLog, FaultTicket, CriticalFaultTicket
)


class LabPulseController:
    """Application Controller abstracting SQLite3 database and file export services."""

    def __init__(self, db_path: str = None, export_dir: str = "exports"):
        self.__db_path = db_path or os.getenv("LABPULSE_DB_PATH", "labpulse.db")
        self.__export_dir = export_dir
        os.makedirs(self.__export_dir, exist_ok=True)
        self.__init_database()
        self.__seed_initial_data()

    def __get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.__db_path)

    @staticmethod
    def _hash_secret(raw_secret: str) -> str:
        return hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()

    def __init_database(self) -> None:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    meta_info TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workstations (
                    pc_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    condition_notes TEXT NOT NULL,
                    current_user TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_logs (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pc_id TEXT NOT NULL,
                    check_in_time TEXT NOT NULL,
                    pre_condition TEXT NOT NULL,
                    check_out_time TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fault_tickets (
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pc_id TEXT NOT NULL,
                    reported_by TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def __seed_initial_data(self) -> None:
        student_pin = os.getenv("DEMO_STUDENT_PIN", "1234")
        instructor_pin = os.getenv("DEMO_INSTRUCTOR_PIN", "2345")
        custodian_pin = os.getenv("DEMO_CUSTODIAN_PIN", "9999")

        default_users = [
            ("2026-0001", "Alex Rivera", self._hash_secret(student_pin), "Student", "BSIT"),
            ("2026-0002", "Jamie Santos", self._hash_secret(student_pin), "Student", "BSCS"),
            ("INST-101", "Prof. Evelyn Cruz", self._hash_secret(instructor_pin), "Instructor", "IT Department"),
            ("CUST-001", "Engr. Marco Reyes", self._hash_secret(custodian_pin), "LabCustodian", "Day Shift"),
        ]

        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", default_users)

            cursor.execute("SELECT COUNT(*) FROM workstations")
            if cursor.fetchone()[0] == 0:
                pcs = [(f"PC-{i:02d}", "Available", "Healthy / Verified", None) for i in range(1, 13)]
                cursor.executemany("INSERT INTO workstations VALUES (?, ?, ?, ?)", pcs)
            conn.commit()

    def authenticate_user(self, user_id: str, raw_password: str) -> User | None:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, full_name, password_hash, role, meta_info FROM users WHERE user_id = ?",
                (user_id.strip(),)
            )
            row = cursor.fetchone()

        if not row:
            return None

        uid, full_name, pwd_hash, role, meta = row
        if role == "Student":
            user_obj = Student(uid, full_name, pwd_hash, program=meta or "BSIT")
        elif role == "Instructor":
            user_obj = Instructor(uid, full_name, pwd_hash, department=meta or "IT Dept")
        elif role == "LabCustodian":
            user_obj = LabCustodian(uid, full_name, pwd_hash, shift=meta or "Day Shift")
        else:
            return None

        return user_obj if user_obj.verify_password(raw_password) else None

    def register_user(self, user_id: str, full_name: str, raw_password: str, role: str, meta_info: str) -> str:
        """Validates and registers a new user account into the SQLite3 database."""
        user_id = user_id.strip()
        full_name = full_name.strip()
        meta_info = meta_info.strip()

        if not user_id or not full_name or not raw_password:
            raise ValueError("User ID, Full Name, and Password/PIN are required.")
        if len(raw_password) < 4:
            raise ValueError("Password/PIN must be at least 4 characters long.")
        if role not in ("Student", "Instructor", "LabCustodian"):
            raise ValueError("Invalid role selected.")

        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                raise ValueError(f"Account with ID '{user_id}' already exists.")

            pwd_hash = self._hash_secret(raw_password)
            if not meta_info:
                meta_info = "BSIT" if role == "Student" else ("IT Department" if role == "Instructor" else "Day Shift")

            cursor.execute(
                "INSERT INTO users (user_id, full_name, password_hash, role, meta_info) VALUES (?, ?, ?, ?, ?)",
                (user_id, full_name, pwd_hash, role, meta_info)
            )
            conn.commit()

        return f"Account created for {full_name} ({role} — {user_id}). You can now log in!"

    def get_user_by_id(self, user_id: str) -> User | None:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, full_name, password_hash, role, meta_info FROM users WHERE user_id = ?",
                (user_id.strip(),)
            )
            row = cursor.fetchone()

        if not row:
            return None

        uid, full_name, pwd_hash, role, meta = row
        if role == "Student":
            return Student(uid, full_name, pwd_hash, program=meta or "BSIT")
        elif role == "Instructor":
            return Instructor(uid, full_name, pwd_hash, department=meta or "IT Dept")
        elif role == "LabCustodian":
            return LabCustodian(uid, full_name, pwd_hash, shift=meta or "Day Shift")
        return None

    def get_all_workstations(self) -> list[Workstation]:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pc_id, status, condition_notes, current_user FROM workstations ORDER BY pc_id")
            return [Workstation(*row) for row in cursor.fetchall()]

    def get_workstation(self, pc_id: str) -> Workstation | None:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT pc_id, status, condition_notes, current_user FROM workstations WHERE pc_id = ?",
                (pc_id,)
            )
            row = cursor.fetchone()
            return Workstation(*row) if row else None

    def _save_workstation(self, ws: Workstation) -> None:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE workstations
                SET status = ?, condition_notes = ?, current_user = ?
                WHERE pc_id = ?
            """, (ws.get_status(), ws.get_condition_notes(), ws.get_current_user(), ws.get_pc_id()))
            conn.commit()

    def check_in_workstation(self, user_id: str, pc_id: str, pre_condition: str) -> str:
        ws = self.get_workstation(pc_id)
        if not ws:
            raise ValueError(f"Workstation {pc_id} does not exist.")
        if ws.get_status() != "Available":
            raise ValueError(f"{pc_id} is currently '{ws.get_status()}' and cannot be checked into.")

        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pc_id FROM workstations WHERE current_user = ?", (user_id,))
            existing = cursor.fetchone()
            if existing:
                raise ValueError(f"User {user_id} already has an active session on {existing[0]}.")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.set_status("Occupied")
            ws.set_current_user(user_id)
            ws.set_condition_notes(f"Pre-check: {pre_condition}")
            self._save_workstation(ws)

            cursor.execute("""
                INSERT INTO session_logs (user_id, pc_id, check_in_time, pre_condition, check_out_time)
                VALUES (?, ?, ?, ?, NULL)
            """, (user_id, pc_id, timestamp, pre_condition))
            conn.commit()

        return f"Check-In Confirmed: {user_id} assigned to {pc_id} at {timestamp}."

    def check_out_workstation(self, user_id: str, pc_id: str, force_override: bool = False) -> str:
        ws = self.get_workstation(pc_id)
        if not ws:
            raise ValueError(f"Workstation {pc_id} not found.")
        if ws.get_status() != "Occupied":
            raise ValueError(f"{pc_id} is not currently occupied.")
        if ws.get_current_user() != user_id and not force_override:
            raise PermissionError(f"{pc_id} is checked in by {ws.get_current_user()}. You cannot check it out.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws.set_status("Available")
        ws.set_current_user(None)
        ws.set_condition_notes("Operational")
        self._save_workstation(ws)

        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE session_logs
                SET check_out_time = ?
                WHERE pc_id = ? AND check_out_time IS NULL
            """, (timestamp, pc_id))
            conn.commit()

        return f"Check-Out Confirmed: {pc_id} released at {timestamp}."

    def submit_fault_ticket(self, reported_by: str, pc_id: str, category: str,
                            severity: str, description: str) -> str:
        if not description.strip():
            raise ValueError("Please provide a fault description.")

        ws = self.get_workstation(pc_id)
        if not ws:
            raise ValueError(f"Workstation {pc_id} not found.")

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fault_tickets (pc_id, reported_by, category, severity, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'Open', ?)
            """, (pc_id, reported_by, category, severity, description.strip(), created_at))
            ticket_id = cursor.lastrowid

            if severity in ("High", "Critical") and ws.get_status() == "Occupied":
                cursor.execute("""
                    UPDATE session_logs
                    SET check_out_time = ?
                    WHERE pc_id = ? AND check_out_time IS NULL
                """, (created_at, pc_id))
            conn.commit()

        if severity in ("High", "Critical"):
            ticket = CriticalFaultTicket(ticket_id, pc_id, reported_by, category, severity, description.strip(), "Open", created_at)
        else:
            ticket = FaultTicket(ticket_id, pc_id, reported_by, category, severity, description.strip(), "Open", created_at)

        result_message = ticket.processAction(ws)
        self._save_workstation(ws)
        return result_message

    def resolve_fault_ticket(self, ticket_id: int, custodian_id: str) -> str:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pc_id, status FROM fault_tickets WHERE ticket_id = ?", (ticket_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Ticket #{ticket_id} does not exist.")
            pc_id, status = row
            if status == "Resolved":
                raise ValueError(f"Ticket #{ticket_id} is already resolved.")

            cursor.execute("UPDATE fault_tickets SET status = 'Resolved' WHERE ticket_id = ?", (ticket_id,))
            conn.commit()

        ws = self.get_workstation(pc_id)
        if ws:
            ws.set_status("Available")
            ws.set_current_user(None)
            ws.set_condition_notes(f"Repaired & verified by {custodian_id}")
            self._save_workstation(ws)

        return f"Ticket #{ticket_id} resolved by {custodian_id}. {pc_id} restored to 'Available'."

    def get_recent_sessions(self) -> list[SessionLog]:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, user_id, pc_id, check_in_time, pre_condition, check_out_time
                FROM session_logs
                ORDER BY session_id DESC LIMIT 50
            """)
            return [SessionLog(*row) for row in cursor.fetchall()]

    def get_fault_tickets(self) -> list[FaultTicket]:
        with self.__get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ticket_id, pc_id, reported_by, category, severity, description, status, created_at
                FROM fault_tickets
                ORDER BY ticket_id DESC LIMIT 50
            """)
            return [FaultTicket(*row) for row in cursor.fetchall()]

    def export_all_records(self) -> str:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = os.path.join(self.__export_dir, f"utilization_logs_{stamp}.csv")
        ticket_file = os.path.join(self.__export_dir, f"maintenance_records_{stamp}.csv")

        sessions = self.get_recent_sessions()
        with open(session_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Session ID", "User ID", "PC ID", "Check-In Time", "Pre-Session Condition", "Check-Out Time"])
            for s in sessions:
                writer.writerow([
                    s.get_session_id(), s.get_user_id(), s.get_pc_id(),
                    s.get_check_in_time(), s.get_pre_condition(), s.get_check_out_time() or "Active"
                ])

        tickets = self.get_fault_tickets()
        with open(ticket_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Ticket ID", "PC ID", "Reported By", "Category", "Severity", "Description", "Status", "Created At"])
            for t in tickets:
                writer.writerow([
                    t.get_ticket_id(), t.get_pc_id(), t.get_reported_by(),
                    t.get_category(), t.get_severity(), t.get_description(),
                    t.get_status(), t.get_created_at()
                ])

        return f"Exported {len(sessions)} session logs and {len(tickets)} fault records to '{self.__export_dir}/'."