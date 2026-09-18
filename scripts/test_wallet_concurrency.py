import os
import sys
import threading
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from apps.billing.services import WalletService, InsufficientCreditsError

User = get_user_model()

def run_stress_test():
    print("🧪 [Stress Test] Testing Wallet Concurrency with PostgreSQL SELECT ... FOR UPDATE...")

    # Create a fresh test user with exactly 100.00 credits
    test_user, _ = User.objects.get_or_create(
        username='concurrency_test_user',
        defaults={'email': 'test@nexmedia.local'}
    )
    test_user.standard_credits = Decimal('100.0000')
    test_user.premium_credits = Decimal('0.0000')
    test_user.save()

    total_threads = 50
    charge_per_thread = Decimal('2.0000')
    # 50 threads * 2.00 = exactly 100.00 credits should be deducted, leaving exactly 0.00!

    successful_debits = 0
    insufficient_count = 0
    lock = threading.Lock()

    def debit_worker(thread_num):
        nonlocal successful_debits, insufficient_count
        # Close connection to force thread-specific connection pool usage
        connection.close()
        try:
            WalletService.validate_and_charge(
                user_id=str(test_user.id),
                cost=charge_per_thread,
                tool_name=f"thread_test_{thread_num}",
                allow_premium=False
            )
            with lock:
                successful_debits += 1
        except InsufficientCreditsError:
            with lock:
                insufficient_count += 1
        except Exception as e:
            print(f"  ❌ Thread {thread_num} encountered unexpected error: {e}")

    threads = [threading.Thread(target=debit_worker, args=(i,)) for i in range(total_threads)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Re-fetch user
    connection.close()
    updated_user = User.objects.get(id=test_user.id)

    print(f"  ✓ Threads launched: {total_threads}")
    print(f"  ✓ Successful debits: {successful_debits}")
    print(f"  ✓ Insufficient credit rejections: {insufficient_count}")
    print(f"  ✓ Final Standard Credits: {updated_user.standard_credits} (Expected: 0.0000)")

    assert updated_user.standard_credits == Decimal('0.0000'), f"Balance mismatch! Got {updated_user.standard_credits}"
    assert successful_debits == 50, f"Expected 50 debits, got {successful_debits}"
    print("🎉 Concurrency Test PASSED! Zero race conditions, zero double spending, perfect row-level lock.")

    # Now test an extra debit: should strictly fail with InsufficientCreditsError
    try:
        WalletService.validate_and_charge(
            user_id=str(test_user.id),
            cost=Decimal('1.0000'),
            tool_name="overdraft_test",
            allow_premium=False
        )
        raise AssertionError("Failed: Overdraft was permitted on empty wallet!")
    except InsufficientCreditsError:
        print("  ✓ Overdraft protection verified: empty wallet correctly rejected.")

    # Test refunding
    WalletService.refund(
        user_id=str(test_user.id),
        standard_amount=Decimal('10.0000'),
        premium_amount=Decimal('0.0000'),
        tool_name="test_refund",
        reason="Verification of refund mechanism"
    )
    refunded_user = User.objects.get(id=test_user.id)
    assert refunded_user.standard_credits == Decimal('10.0000'), f"Refund failed: {refunded_user.standard_credits}"
    print("  ✓ Refund mechanism verified: balance accurately restored to 10.0000.")

    print("🏁 All Wallet & Concurrency tests PASSED!")

if __name__ == '__main__':
    run_stress_test()
