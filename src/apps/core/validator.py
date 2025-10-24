from django.core.exceptions import ValidationError
from django.utils import timezone

from src.apps.core.models import (
    RepairOrders,
    RepairsStatus,
    Payments,
    PaymentsStatus,
    Rentals,
    RentalsStatus
)


def _ensure_next_step(current_align: int, target_align: int, *, one_step=True):
    if target_align <= current_align:
        raise ValidationError("Status can only move forward.")
    if one_step and (target_align - current_align) != 10:
        raise ValidationError("You must move to the next step only.")

def _is_terminal(status_text: str) -> bool:
    return status_text.lower() in {"paid", "verified", "failed", "refunded", "returned"}


def validate_repair_transition(instance: RepairOrders, target_status: RepairsStatus):
    cur = instance.status
    tgt = target_status
    if _is_terminal(cur.payment_status_text):
        raise ValidationError(f"'{cur.payment_status_text}' is terminal; cannot change.")

    if tgt.payment_status_text.lower() == "paid":
        raise ValidationError("You cannot set 'Paid' manually. Use payment verification flow.")

    _ensure_next_step(cur.payment_status_align, tgt.payment_status_align, one_step=True)


def apply_completed_timestamp_if_needed(instance: RepairOrders, target_status: RepairsStatus):
    if target_status.payment_status_text.lower() == "completed" and instance.completed_at is None:
        instance.completed_at = timezone.now()


def validate_payment_initiate(repair: RepairOrders):
    cur = repair.status
    if cur.payment_status_text.lower() != "completed":
        raise ValidationError("Payment can be initiated only after repair is COMPLETED.")

    existing = getattr(repair, "payment", None)
    if existing and existing.status.payment_status_text.lower() in {"initiated", "verified"}:
        raise ValidationError("A payment already exists for this repair.")

def validate_payment_transition(payment: Payments, target_status: PaymentsStatus):
    cur = payment.status
    tgt = target_status

    if cur.payment_status_text.lower() != "initiated":
        raise ValidationError("Only 'initiated' payments can transition.")

    allowed = {"verified", "failed", "refunded"}
    if tgt.payment_status_text.lower() not in allowed:
        raise ValidationError("Target payment status must be one of: verified, failed, refunded.")

    _ensure_next_step(cur.payment_status_align, tgt.payment_status_align, one_step=False)


def validate_rental_transition(rental: Rentals, target_status: RentalsStatus):
    cur = rental.status
    tgt = target_status

    cur_txt = cur.payment_status_text.lower()
    tgt_txt = tgt.payment_status_text.lower()

    if cur_txt == "booked" and tgt_txt in {"active", "canceled"}:
        _ensure_next_step(cur.payment_status_align, tgt.payment_status_align, one_step=False)
        return

    if cur_txt == "active" and tgt_txt == "returned":
        _ensure_next_step(cur.payment_status_align, tgt.payment_status_align, one_step=True)
        return

    raise ValidationError(f"Invalid rental transition: {cur.payment_status_text} -> {tgt.payment_status_text}")
