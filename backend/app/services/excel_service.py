"""
Excel-backed scheduling service utilities.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import random
import string
from typing import Any, Dict, List, Optional

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


EXCEL_FILENAME = "scheduling_data.xlsx"
AVAILABILITY_SHEET = "Availability"
SCHEDULED_MEETINGS_SHEET = "Scheduled_Meetings"


def _resolve_excel_path() -> Path:
    app_dir = Path(__file__).resolve().parents[1]  # backend/app/
    base_dir = Path(__file__).resolve().parents[2]  # backend/
    candidates = [
        app_dir / "data" / EXCEL_FILENAME,
        base_dir / "data" / EXCEL_FILENAME,
        base_dir / "backend" / "data" / EXCEL_FILENAME,
    ]
    for file_path in candidates:
        if file_path.exists():
            return file_path
    raise FileNotFoundError(
        f"Could not find {EXCEL_FILENAME}. Tried: {', '.join(str(p) for p in candidates)}"
    )


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalized_header(value: Any) -> str:
    return _normalize(value).lower()


def _sheet_by_name(workbook: Workbook, expected_name: str) -> Worksheet:
    expected = expected_name.strip().lower()
    for sheet_name in workbook.sheetnames:
        if sheet_name.strip().lower() == expected:
            return workbook[sheet_name]
    raise ValueError(f"Sheet '{expected_name}' not found in workbook.")


def _headers_map(sheet: Worksheet) -> Dict[str, int]:
    headers: Dict[str, int] = {}
    for col_idx, cell in enumerate(sheet[1], start=1):
        header = _normalized_header(cell.value)
        if header:
            headers[header] = col_idx
    return headers


def _row_value(sheet: Worksheet, row_idx: int, headers: Dict[str, int], key: str) -> str:
    col_idx = headers.get(key.lower())
    if not col_idx:
        return ""
    return _normalize(sheet.cell(row=row_idx, column=col_idx).value)


def _ensure_meetings_headers(sheet: Worksheet) -> Dict[str, int]:
    expected_headers = [
        "candidate_name",
        "meeting_type",
        "interviewer_name",
        "interviewer_role",
        "date",
        "time",
        "status",
        "booked_by",
        "booked_at",
        "meeting_link",
    ]
    headers = _headers_map(sheet)

    if not headers:
        sheet.append(expected_headers)
        return {header: idx for idx, header in enumerate(expected_headers, start=1)}

    missing = [header for header in expected_headers if header not in headers]
    if missing:
        raise ValueError(
            f"'{SCHEDULED_MEETINGS_SHEET}' sheet is missing required headers: {missing}"
        )
    return headers


def _generate_meeting_link() -> str:
    chunk_1 = "".join(random.choices(string.ascii_lowercase, k=3))
    chunk_2 = "".join(random.choices(string.ascii_lowercase, k=4))
    return f"https://meet.google.com/onboardiq-{chunk_1}-{chunk_2}"


def get_all_available_slots(person_name: str) -> List[Dict[str, str]]:
    workbook = load_workbook(_resolve_excel_path())
    availability = _sheet_by_name(workbook, AVAILABILITY_SHEET)
    headers = _headers_map(availability)

    target_name = person_name.strip().lower()
    slots: List[Dict[str, str]] = []

    for row_idx in range(2, availability.max_row + 1):
        name = _row_value(availability, row_idx, headers, "name")
        available = _row_value(availability, row_idx, headers, "available").upper()
        if name.lower() == target_name and available == "YES":
            slots.append(
                {
                    "name": name,
                    "role": _row_value(availability, row_idx, headers, "role"),
                    "date": _row_value(availability, row_idx, headers, "date"),
                    "time": _row_value(availability, row_idx, headers, "time"),
                }
            )
    return slots


def get_first_available_slot(person_name: str) -> Optional[Dict[str, str]]:
    slots = get_all_available_slots(person_name)
    return slots[0] if slots else None


def get_all_interviewers(role_filter: str = None) -> List[Dict[str, str]]:
    workbook = load_workbook(_resolve_excel_path())
    availability = _sheet_by_name(workbook, AVAILABILITY_SHEET)
    headers = _headers_map(availability)

    target_role = role_filter.strip().lower() if role_filter else None
    seen = set()
    interviewers: List[Dict[str, str]] = []

    for row_idx in range(2, availability.max_row + 1):
        name = _row_value(availability, row_idx, headers, "name")
        role = _row_value(availability, row_idx, headers, "role")
        if not name:
            continue
        if target_role and role.lower() != target_role:
            continue
        key = (name.lower(), role.lower())
        if key in seen:
            continue
        seen.add(key)
        interviewers.append({"name": name, "role": role})

    interviewers.sort(key=lambda person: (person["role"].lower(), person["name"].lower()))
    return interviewers


def book_slot(
    candidate_name: str,
    meeting_type: str,
    interviewer_name: str,
    date: str,
    time: str,
    booked_by: str,
) -> Dict[str, Any]:
    workbook = load_workbook(_resolve_excel_path())
    availability = _sheet_by_name(workbook, AVAILABILITY_SHEET)
    availability_headers = _headers_map(availability)

    target_name = interviewer_name.strip().lower()
    target_date = date.strip()
    target_time = time.strip()

    matched_row = None
    interviewer_role = ""

    for row_idx in range(2, availability.max_row + 1):
        name = _row_value(availability, row_idx, availability_headers, "name")
        slot_date = _row_value(availability, row_idx, availability_headers, "date")
        slot_time = _row_value(availability, row_idx, availability_headers, "time")
        if name.lower() == target_name and slot_date == target_date and slot_time == target_time:
            matched_row = row_idx
            interviewer_role = _row_value(availability, row_idx, availability_headers, "role")
            break

    if matched_row is None:
        return {
            "success": False,
            "error": "slot_not_found",
            "message": "Slot not found for the selected interviewer/date/time.",
        }

    available_col = availability_headers.get("available")
    if not available_col:
        raise ValueError(f"'{AVAILABILITY_SHEET}' sheet is missing the 'available' column.")

    current_status = _normalize(
        availability.cell(row=matched_row, column=available_col).value
    ).upper()
    if current_status != "YES":
        return {
            "success": False,
            "error": "slot_unavailable",
            "message": "Selected slot is already booked.",
        }

    availability.cell(row=matched_row, column=available_col, value="NO")

    scheduled_sheet = _sheet_by_name(workbook, SCHEDULED_MEETINGS_SHEET)
    scheduled_headers = _ensure_meetings_headers(scheduled_sheet)

    booking = {
        "candidate_name": candidate_name,
        "meeting_type": meeting_type,
        "interviewer_name": interviewer_name,
        "interviewer_role": interviewer_role,
        "date": date,
        "time": time,
        "status": "confirmed",
        "booked_by": booked_by,
        "booked_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "meeting_link": _generate_meeting_link(),
    }

    row_values = [booking[header] for header in sorted(scheduled_headers, key=scheduled_headers.get)]
    scheduled_sheet.append(row_values)
    workbook.save(_resolve_excel_path())

    return {"success": True, "booking": booking}


def get_meetings_for_candidate(candidate_name: str) -> List[Dict[str, str]]:
    workbook = load_workbook(_resolve_excel_path())
    scheduled_sheet = _sheet_by_name(workbook, SCHEDULED_MEETINGS_SHEET)
    headers = _headers_map(scheduled_sheet)

    normalized_candidate_name = candidate_name.strip().lower()
    meetings: List[Dict[str, str]] = []
    for row_idx in range(2, scheduled_sheet.max_row + 1):
        sheet_candidate_name = _row_value(scheduled_sheet, row_idx, headers, "candidate_name")
        if sheet_candidate_name.lower() != normalized_candidate_name:
            continue
        meetings.append(
            {
                "candidate_name": sheet_candidate_name,
                "meeting_type": _row_value(scheduled_sheet, row_idx, headers, "meeting_type"),
                "interviewer_name": _row_value(
                    scheduled_sheet, row_idx, headers, "interviewer_name"
                ),
                "interviewer_role": _row_value(
                    scheduled_sheet, row_idx, headers, "interviewer_role"
                ),
                "date": _row_value(scheduled_sheet, row_idx, headers, "date"),
                "time": _row_value(scheduled_sheet, row_idx, headers, "time"),
                "status": _row_value(scheduled_sheet, row_idx, headers, "status"),
                "booked_by": _row_value(scheduled_sheet, row_idx, headers, "booked_by"),
                "booked_at": _row_value(scheduled_sheet, row_idx, headers, "booked_at"),
                "meeting_link": _row_value(scheduled_sheet, row_idx, headers, "meeting_link"),
            }
        )
    return meetings
