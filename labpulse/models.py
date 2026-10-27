import hashlib
from abc import ABC, abstractmethod
from datetime import datetime


class User(ABC):
    """Abstract Base Class representing an authenticated LabPulse user."""

    def __init__(self, user_id: str, full_name: str, password_hash: str, role: str):
        self.__user_id = user_id
        self.__full_name = full_name
        self.__password_hash = password_hash
        self.__role = role

    def get_user_id(self) -> str:
        return self.__user_id

    def get_full_name(self) -> str:
        return self.__full_name

    def get_role(self) -> str:
        return self.__role

    def set_full_name(self, new_name: str) -> None:
        if new_name.strip():
            self.__full_name = new_name.strip()

    def verify_password(self, raw_password: str) -> bool:
        hashed_input = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
        return self.__password_hash == hashed_input

    def set_password(self, new_raw_password: str) -> None:
        if len(new_raw_password) < 4:
            raise ValueError("Password/PIN must be at least 4 characters.")
        self.__password_hash = hashlib.sha256(new_raw_password.encode("utf-8")).hexdigest()

    @abstractmethod
    def loadDashboard(self) -> dict:
        """Polymorphic method returning role-specific UI permissions."""
        pass

    @abstractmethod
    def processAction(self, controller, action_type: str, payload: dict) -> str:
        """Polymorphic method executing role-specific operations."""
        pass


class Student(User):
    """Student role inheriting from User."""

    def __init__(self, user_id: str, full_name: str, password_hash: str, program: str = "BSIT"):
        super().__init__(user_id, full_name, password_hash, role="Student")
        self.__program = program

    def get_program(self) -> str:
        return self.__program

    def loadDashboard(self) -> dict:
        return {
            "title": f"Student Portal — {self.get_full_name()} ({self.__program})",
            "can_resolve_fault": False,
            "can_export_logs": False,
        }

    def processAction(self, controller, action_type: str, payload: dict) -> str:
        if action_type == "CHECK_IN":
            return controller.check_in_workstation(
                self.get_user_id(), payload["pc_id"], payload["pre_condition"]
            )
        elif action_type == "CHECK_OUT":
            return controller.check_out_workstation(self.get_user_id(), payload["pc_id"])
        elif action_type == "REPORT_FAULT":
            return controller.submit_fault_ticket(
                self.get_user_id(),
                payload["pc_id"],
                payload["category"],
                payload["severity"],
                payload["description"]
            )
        raise PermissionError("Students are not authorized to perform this action.")


class Instructor(User):
    """Instructor role inheriting from User with log export privileges."""

    def __init__(self, user_id: str, full_name: str, password_hash: str, department: str = "IT Department"):
        super().__init__(user_id, full_name, password_hash, role="Instructor")
        self.__department = department

    def get_department(self) -> str:
        return self.__department

    def loadDashboard(self) -> dict:
        return {
            "title": f"Instructor Console — {self.get_full_name()} ({self.__department})",
            "can_resolve_fault": False,
            "can_export_logs": True,
        }

    def processAction(self, controller, action_type: str, payload: dict) -> str:
        if action_type == "CHECK_IN":
            return controller.check_in_workstation(
                self.get_user_id(), payload["pc_id"], payload["pre_condition"]
            )
        elif action_type == "CHECK_OUT":
            return controller.check_out_workstation(self.get_user_id(), payload["pc_id"])
        elif action_type == "REPORT_FAULT":
            return controller.submit_fault_ticket(
                self.get_user_id(),
                payload["pc_id"],
                payload["category"],
                payload["severity"],
                payload["description"]
            )
        elif action_type == "EXPORT_LOGS":
            return controller.export_all_records()
        raise PermissionError("Action not permitted for Instructor role.")


class LabCustodian(User):
    """LabCustodian role inheriting from User with full maintenance and repair control."""

    def __init__(self, user_id: str, full_name: str, password_hash: str, shift: str = "Day Shift"):
        super().__init__(user_id, full_name, password_hash, role="LabCustodian")
        self.__shift = shift

    def get_shift(self) -> str:
        return self.__shift

    def loadDashboard(self) -> dict:
        return {
            "title": f"Lab Custodian Operations — {self.get_full_name()} ({self.__shift})",
            "can_resolve_fault": True,
            "can_export_logs": True,
        }

    def processAction(self, controller, action_type: str, payload: dict) -> str:
        if action_type == "CHECK_IN":
            return controller.check_in_workstation(
                self.get_user_id(), payload["pc_id"], payload["pre_condition"]
            )
        elif action_type == "CHECK_OUT":
            return controller.check_out_workstation(
                self.get_user_id(), payload["pc_id"], force_override=True
            )
        elif action_type == "REPORT_FAULT":
            return controller.submit_fault_ticket(
                self.get_user_id(),
                payload["pc_id"],
                payload["category"],
                payload["severity"],
                payload["description"]
            )
        elif action_type == "RESOLVE_FAULT":
            return controller.resolve_fault_ticket(payload["ticket_id"], self.get_user_id())
        elif action_type == "EXPORT_LOGS":
            return controller.export_all_records()
        raise ValueError(f"Unknown action type: {action_type}")


class Workstation:
    """Encapsulated model representing a laboratory workstation."""

    VALID_STATUSES = ("Available", "Occupied", "Maintenance")

    def __init__(self, pc_id: str, status: str = "Available", condition_notes: str = "Operational", current_user: str = None):
        self.__pc_id = pc_id
        self.__status = status if status in self.VALID_STATUSES else "Available"
        self.__condition_notes = condition_notes
        self.__current_user = current_user

    def get_pc_id(self) -> str:
        return self.__pc_id

    def get_status(self) -> str:
        return self.__status

    def set_status(self, new_status: str) -> None:
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid workstation status: {new_status}")
        self.__status = new_status

    def get_condition_notes(self) -> str:
        return self.__condition_notes

    def set_condition_notes(self, notes: str) -> None:
        self.__condition_notes = notes.strip() or "Operational"

    def get_current_user(self) -> str | None:
        return self.__current_user

    def set_current_user(self, user_id: str | None) -> None:
        self.__current_user = user_id


class SessionLog:
    """Encapsulated model for tracking workstation utilization sessions."""

    def __init__(self, session_id: int, user_id: str, pc_id: str, check_in_time: str,
                 pre_condition: str, check_out_time: str = None):
        self.__session_id = session_id
        self.__user_id = user_id
        self.__pc_id = pc_id
        self.__check_in_time = check_in_time
        self.__pre_condition = pre_condition
        self.__check_out_time = check_out_time

    def get_session_id(self) -> int:
        return self.__session_id

    def get_user_id(self) -> str:
        return self.__user_id

    def get_pc_id(self) -> str:
        return self.__pc_id

    def get_check_in_time(self) -> str:
        return self.__check_in_time

    def get_pre_condition(self) -> str:
        return self.__pre_condition

    def get_check_out_time(self) -> str | None:
        return self.__check_out_time

    def close_session(self, timestamp: str) -> None:
        self.__check_out_time = timestamp


class FaultTicket:
    """Base class for hardware/software fault tickets."""

    def __init__(self, ticket_id: int, pc_id: str, reported_by: str, category: str,
                 severity: str, description: str, status: str = "Open", created_at: str = None):
        self.__ticket_id = ticket_id
        self.__pc_id = pc_id
        self.__reported_by = reported_by
        self.__category = category
        self.__severity = severity
        self.__description = description
        self.__status = status
        self.__created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_ticket_id(self) -> int:
        return self.__ticket_id

    def get_pc_id(self) -> str:
        return self.__pc_id

    def get_reported_by(self) -> str:
        return self.__reported_by

    def get_category(self) -> str:
        return self.__category

    def get_severity(self) -> str:
        return self.__severity

    def get_description(self) -> str:
        return self.__description

    def get_status(self) -> str:
        return self.__status

    def set_status(self, new_status: str) -> None:
        if new_status not in ("Open", "Resolved"):
            raise ValueError("Invalid ticket status.")
        self.__status = new_status

    def get_created_at(self) -> str:
        return self.__created_at

    def processAction(self, workstation: Workstation) -> str:
        """Polymorphic handling for Low/Medium faults: flags note without locking PC."""
        workstation.set_condition_notes(f"[{self.__severity} {self.__category}] {self.__description}")
        return (
            f"Ticket #{self.__ticket_id} logged ({self.__severity}). "
            f"{workstation.get_pc_id()} flagged for inspection but remains operational."
        )


class CriticalFaultTicket(FaultTicket):
    """Subclass overriding processAction() for High/Critical severity faults."""

    def processAction(self, workstation: Workstation) -> str:
        """Polymorphic handling for High/Critical faults: locks PC to Maintenance."""
        workstation.set_status("Maintenance")
        workstation.set_current_user(None)
        workstation.set_condition_notes(f"[CRITICAL {self.get_category()}] {self.get_description()}")
        return (
            f"CRITICAL Ticket #{self.get_ticket_id()} filed! "
            f"{workstation.get_pc_id()} automatically locked to 'Maintenance' status."
        )