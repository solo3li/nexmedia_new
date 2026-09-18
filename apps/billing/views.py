from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.billing.models import Plan, Payment, ManualPaymentMethod
from apps.core.storage import storage_service
from apps.billing.services import WalletService

def pricing_view(request):
    plans = Plan.objects.filter(is_active=True).order_by('price_usd')
    return render(request, 'billing/pricing.html', {'plans': plans})

@login_required
def checkout_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    manual_methods = ManualPaymentMethod.objects.filter(is_active=True)

    if request.method == 'POST':
        method = request.POST.get('method')
        currency = request.POST.get('currency', 'USD')
        amount = plan.price_egp if currency == 'EGP' else plan.price_usd

        if method == 'manual':
            receipt_file = request.FILES.get('receipt')
            receipt_url = ""
            if receipt_file:
                object_name = f"receipts/{request.user.id}_{receipt_file.name}"
                storage_service.upload_file_bytes(
                    receipt_file.read(),
                    object_name,
                    receipt_file.content_type
                )
                receipt_url = storage_service.get_presigned_url(object_name)

            payment = Payment.objects.create(
                user=request.user,
                plan=plan,
                amount=amount,
                currency=currency,
                method='manual',
                status='pending',
                receipt_url=receipt_url,
                admin_notes="Manual bank transfer / wallet upload"
            )
            messages.success(request, 'تم إرسال إيصال الدفع بنجاح! سيتم تفعيل الخطة بعد مراجعة الإدارة. / Receipt submitted for admin review.')
            return redirect('profile')

        # Automated sandbox payment activation for testing/demo
        elif method in ('paymob', 'paypal'):
            payment = Payment.objects.create(
                user=request.user,
                plan=plan,
                amount=amount,
                currency=currency,
                method=method,
                status='completed',
                transaction_id=f"TX-{method.upper()}-DEMO"
            )
            WalletService.assign_plan(str(request.user.id), str(plan.id), reset_to_zero=False)
            messages.success(request, f'تم الدفع وتفعيل خطة {plan.name} بنجاح! / Plan {plan.name} activated!')
            return redirect('dashboard')

    return render(request, 'billing/checkout.html', {
        'plan': plan,
        'manual_methods': manual_methods
    })
