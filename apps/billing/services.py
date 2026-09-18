from decimal import Decimal
from datetime import datetime, timedelta, timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.billing.models import Plan, Subscription, WalletTransaction
from apps.core.centrifugo import centrifugo_service
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class InsufficientCreditsError(Exception):
    pass

class WalletService:
    @staticmethod
    def validate_and_charge(user_id: str, cost: Decimal, tool_name: str, allow_premium: bool = True) -> dict:
        """
        Thread-safe wallet deduction using PostgreSQL SELECT ... FOR UPDATE.
        Deducts from Standard Credits first; remainder from Premium Credits if permitted.
        Returns a dict of deducted amounts: {'standard_deducted': ..., 'premium_deducted': ...}
        """
        cost = Decimal(str(cost))
        if cost <= Decimal('0.0000'):
            return {'standard_deducted': Decimal('0.0000'), 'premium_deducted': Decimal('0.0000')}

        with transaction.atomic():
            user = User.objects.select_for_update().get(id=user_id)

            standard_available = user.standard_credits
            premium_available = user.premium_credits

            standard_to_deduct = min(standard_available, cost)
            remaining_cost = cost - standard_to_deduct

            if remaining_cost > Decimal('0.0000'):
                if not allow_premium or premium_available < remaining_cost:
                    raise InsufficientCreditsError(
                        f"Insufficient credits for {tool_name}. Required: {cost}, "
                        f"Standard: {standard_available}, Premium: {premium_available}"
                    )
                premium_to_deduct = remaining_cost
            else:
                premium_to_deduct = Decimal('0.0000')

            # Apply deductions
            user.standard_credits -= standard_to_deduct
            user.premium_credits -= premium_to_deduct
            user.save(update_fields=['standard_credits', 'premium_credits'])

            # Record ledger transactions
            if standard_to_deduct > Decimal('0.0000'):
                WalletTransaction.objects.create(
                    user=user,
                    tool_name=tool_name,
                    wallet_type='standard',
                    amount=-standard_to_deduct,
                    balance_after=user.standard_credits,
                    description=f"Charged for {tool_name}"
                )

            if premium_to_deduct > Decimal('0.0000'):
                WalletTransaction.objects.create(
                    user=user,
                    tool_name=tool_name,
                    wallet_type='premium',
                    amount=-premium_to_deduct,
                    balance_after=user.premium_credits,
                    description=f"Charged for {tool_name} (Premium)"
                )

            # Realtime wallet update push to Centrifugo
            centrifugo_service.notify_user(str(user.id), "WALLET_UPDATED", {
                "standard_credits": float(user.standard_credits),
                "premium_credits": float(user.premium_credits),
            })

            return {
                'standard_deducted': standard_to_deduct,
                'premium_deducted': premium_to_deduct
            }

    @staticmethod
    def refund(user_id: str, standard_amount: Decimal, premium_amount: Decimal, tool_name: str, reason: str = ""):
        """
        Thread-safe refund of debited credits in case of AI worker/provider failure.
        """
        standard_amount = Decimal(str(standard_amount))
        premium_amount = Decimal(str(premium_amount))

        if standard_amount <= Decimal('0.0000') and premium_amount <= Decimal('0.0000'):
            return

        with transaction.atomic():
            user = User.objects.select_for_update().get(id=user_id)
            user.standard_credits += standard_amount
            user.premium_credits += premium_amount
            user.save(update_fields=['standard_credits', 'premium_credits'])

            if standard_amount > Decimal('0.0000'):
                WalletTransaction.objects.create(
                    user=user,
                    tool_name=tool_name,
                    wallet_type='standard',
                    amount=standard_amount,
                    balance_after=user.standard_credits,
                    description=f"Refunded from {tool_name}: {reason}"
                )

            if premium_amount > Decimal('0.0000'):
                WalletTransaction.objects.create(
                    user=user,
                    tool_name=tool_name,
                    wallet_type='premium',
                    amount=premium_amount,
                    balance_after=user.premium_credits,
                    description=f"Refunded from {tool_name}: {reason}"
                )

            centrifugo_service.notify_user(str(user.id), "WALLET_UPDATED", {
                "standard_credits": float(user.standard_credits),
                "premium_credits": float(user.premium_credits),
                "refunded": True,
                "reason": reason
            })

    @staticmethod
    def assign_plan(user_id: str, plan_id: str, reset_to_zero: bool = False) -> Subscription:
        """
        Assigns or renews a subscription plan and distributes credits.
        """
        with transaction.atomic():
            user = User.objects.select_for_update().get(id=user_id)
            plan = Plan.objects.get(id=plan_id)

            now = datetime.now(timezone.utc)
            end_date = now + timedelta(days=plan.duration_days)

            # Deactivate competing active subscriptions
            Subscription.objects.filter(user=user, status='active').update(status='canceled')

            sub = Subscription.objects.create(
                user=user,
                plan=plan,
                status='active',
                start_date=now,
                end_date=end_date
            )

            if reset_to_zero:
                user.standard_credits = plan.standard_credits_grant
                user.premium_credits = plan.premium_credits_grant
            else:
                user.standard_credits += plan.standard_credits_grant
                user.premium_credits += plan.premium_credits_grant

            user.save(update_fields=['standard_credits', 'premium_credits'])

            WalletTransaction.objects.create(
                user=user,
                tool_name="subscription",
                wallet_type="standard",
                amount=plan.standard_credits_grant,
                balance_after=user.standard_credits,
                description=f"Plan credits granted: {plan.name}"
            )

            centrifugo_service.notify_user(str(user.id), "WALLET_UPDATED", {
                "standard_credits": float(user.standard_credits),
                "premium_credits": float(user.premium_credits),
                "plan_name": plan.name
            })

            return sub
