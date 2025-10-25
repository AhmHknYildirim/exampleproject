from celery import shared_task
from django.utils import timezone
from src.apps.core.models import (
    RepairOrders,
    Payments,
    RepairsStatus,
    PaymentsStatus
)

@shared_task
def verify_payment_and_mark_repair_paid(repair_id: int):
    try:
        repair = RepairOrders.objects.get(pk=repair_id, is_active=True)
    except RepairOrders.DoesNotExist:
        return {"ok": False, "reason": "repair_not_found"}

    cur = repair.status
    if getattr(cur, "repair_status_text", "").lower() != "completed":
        return {"ok": False, "reason": "repair_not_completed"}

    payment = getattr(repair, "payment", None)
    if not payment or not payment.is_active:
        return {"ok": False, "reason": "payment_missing"}

    try:
        paid_status = PaymentsStatus.objects.get(payment_status_text__iexact="paid", is_active=True)
    except PaymentsStatus.DoesNotExist:
        return {"ok": False, "reason": "paid_status_missing"}

    if payment.status_id != paid_status.id:
        payment.status = paid_status
        payment.payment_date = timezone.now()
        payment.save(update_fields=["status", "payment_date"])
    return {"ok": True, "repair_id": repair_id}
