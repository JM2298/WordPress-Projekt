from __future__ import annotations

from typing import Any

from django.conf import settings

from backend_api.google_sheets import GoogleSheetsAPIError, append_row


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _categories_to_text(categories: Any) -> str:
    if not isinstance(categories, list):
        return ""

    names: list[str] = []
    for category in categories:
        if isinstance(category, dict):
            name = category.get("name")
            if name:
                names.append(str(name))
    return ", ".join(names)


def _images_to_text(images: Any) -> str:
    if not isinstance(images, list):
        return ""

    links: list[str] = []
    for image in images:
        if not isinstance(image, dict):
            continue
        src = image.get("src")
        if src:
            links.append(str(src))
    return ", ".join(links)


def _is_range_parse_error(exc: GoogleSheetsAPIError) -> bool:
    details = exc.details if isinstance(exc.details, dict) else {}
    response_payload = details.get("response")
    if not isinstance(response_payload, dict):
        return False

    error_payload = response_payload.get("error")
    if not isinstance(error_payload, dict):
        return False

    message = str(error_payload.get("message", "")).lower()
    return "unable to parse range" in message


def _range_without_sheet_name(range_name: str) -> str | None:
    if "!" not in range_name:
        return None
    _, raw_columns = range_name.split("!", 1)
    columns = raw_columns.strip()
    return columns or None


def build_product_sheet_row(product_data: dict[str, Any]) -> list[str]:
    return [
        _stringify(product_data.get("id")),
        _stringify(product_data.get("name")),
        _stringify(product_data.get("type")),
        _stringify(
            product_data.get("price")
            or product_data.get("regular_price")
            or ""
        ),
        _stringify(product_data.get("status")),
        _stringify(product_data.get("date_created")),
        _stringify(product_data.get("permalink")),
        _categories_to_text(product_data.get("categories")),
        _images_to_text(product_data.get("images")),
    ]


def append_product_to_sheet(product_data: dict[str, Any]) -> dict[str, Any]:
    range_name = str(
        getattr(settings, "GOOGLE_SHEETS_PRODUCTS_RANGE", "A:I")
    )
    row = build_product_sheet_row(product_data)

    try:
        return append_row(row=row, range_name=range_name)
    except GoogleSheetsAPIError as exc:
        fallback_range = _range_without_sheet_name(range_name)
        if fallback_range and fallback_range != range_name and _is_range_parse_error(exc):
            return append_row(row=row, range_name=fallback_range)
        raise
