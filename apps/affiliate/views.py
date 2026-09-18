from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.affiliate.models import AffiliateProfile, AffiliatePayout

@login_required
def affiliate_dashboard_view(request):
    profile, _ = AffiliateProfile.objects.get_or_create(user=request.user)
    referrals_count = profile.referrals.count()
    commissions = profile.commissions.all().order_by('-created_at')
    total_earnings = sum(c.amount for c in commissions if c.status in ('available', 'paid'))
    payouts = profile.payouts.all().order_by('-created_at')

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', '0'))
        payout_method = request.POST.get('payout_method', '')
        account_details = request.POST.get('account_details', '')

        if amount > 0 and account_details:
            AffiliatePayout.objects.create(
                referrer=profile,
                amount=amount,
                payout_method=payout_method,
                account_details=account_details,
                status='pending'
            )
            messages.success(request, 'تم إرسال طلب السحب بنجاح! / Payout request submitted successfully!')
            return redirect('affiliate_dashboard')
        else:
            messages.error(request, 'بيانات طلب السحب غير مكتملة / Invalid payout details')

    return render(request, 'affiliate/dashboard.html', {
        'profile': profile,
        'referrals_count': referrals_count,
        'commissions': commissions,
        'total_earnings': total_earnings,
        'payouts': payouts,
    })
