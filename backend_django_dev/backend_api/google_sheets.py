from __future__ import annotations

import json
import os
from typing import Any

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:  # pragma: no cover - handled as runtime configuration error
    Credentials = None
    HttpError = Exception
    build = None


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsConfigurationError(Exception):
    """Raised when required Google Sheets settings are missing or invalid."""


class GoogleSheetsAPIError(Exception):
    """Raised when Google Sheets API returns a transport or API error."""

    def __init__(
        self,
        message: str,
        status_code: int = 502,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details


def _require_env(name: str) -> str:
    value = str(os.getenv(name, "")).strip()
    if not value:
        raise GoogleSheetsConfigurationError(f"Missing {name} setting.")
    return value


def _http_error_details(exc: HttpError) -> dict[str, Any]:
    details: dict[str, Any] = {}
    content = getattr(exc, "content", None)
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    if isinstance(content, str) and content:
        try:
            parsed = json.loads(content)
            details["response"] = parsed
        except json.JSONDecodeError:
            details["response"] = content
    return details


def get_sheets_service():
    if Credentials is None or build is None:
        raise GoogleSheetsConfigurationError(
            "Missing Google Sheets dependencies. Install requirements.txt packages."
        )

    credentials_path = _require_env("GOOGLE_SHEETS_CREDENTIALS")

    try:
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES,
        )
    except (OSError, ValueError) as exc:
        raise GoogleSheetsConfigurationError(
            f"Unable to load service account credentials from {credentials_path}."
        ) from exc

    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def read_sheet(range_name: str = "Arkusz1!A1:D10") -> list[list[Any]]:
    spreadsheet_id = _require_env("GOOGLE_SHEET_ID")
    service = get_sheets_service()
    sheet = service.spreadsheets()

    try:
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        ).execute()
    except HttpError as exc:
        raise GoogleSheetsAPIError(
            "Google Sheets API returned an error while reading sheet data.",
            status_code=getattr(getattr(exc, "resp", None), "status", 502) or 502,
            details=_http_error_details(exc),
        ) from exc
    except Exception as exc:
        raise GoogleSheetsAPIError(
            "Unable to read data from Google Sheets.",
            status_code=502,
            details={"error": str(exc)},
        ) from exc

    values = result.get("values", [])
    return values if isinstance(values, list) else []


def append_row(
    row: list[Any],
    range_name: str = "Arkusz1!A:D",
) -> dict[str, Any]:
    spreadsheet_id = _require_env("GOOGLE_SHEET_ID")
    service = get_sheets_service()
    body = {"values": [row]}

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()
    except HttpError as exc:
        raise GoogleSheetsAPIError(
            "Google Sheets API returned an error while appending a row.",
            status_code=getattr(getattr(exc, "resp", None), "status", 502) or 502,
            details=_http_error_details(exc),
        ) from exc
    except Exception as exc:
        raise GoogleSheetsAPIError(
            "Unable to append row to Google Sheets.",
            status_code=502,
            details={"error": str(exc)},
        ) from exc

    return result
