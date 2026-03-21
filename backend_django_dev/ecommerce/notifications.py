from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q


def registered_user_emails() -> list[str]:
    user_model = get_user_model()
    return list(
        user_model.objects.filter(is_active=True)
        .exclude(Q(email__isnull=True) | Q(email__exact=""))
        .values_list("email", flat=True)
        .distinct()
    )


def send_product_created_email(product_data: dict) -> int:
    recipients = registered_user_emails()
    if not recipients:
        return 0

    product_name = str(product_data.get("name") or "Nowy produkt")
    product_id = product_data.get("id")
    product_price = (
        product_data.get("price")
        or product_data.get("regular_price")
        or "brak danych"
    )
    product_url = str(product_data.get("permalink") or "")

    subject = f"Nowy produkt: {product_name}"
    message_lines = [
        f"Dodano nowy produkt: {product_name}",
        f"ID: {product_id if product_id is not None else 'brak'}",
        f"Cena: {product_price}",
    ]
    if product_url:
        message_lines.append(f"Link: {product_url}")

    send_mail(
        subject=subject,
        message="\n".join(message_lines),
        from_email=None,
        recipient_list=recipients,
        fail_silently=False,
    )
    return len(recipients)
