from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.forms import RegisterForm, LoginForm
from apps.billing.models import Plan
from apps.billing.services import WalletService

User = get_user_model()

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Automatically assign default/free trial plan with starter credits
            default_plan = Plan.objects.filter(is_default_registration_plan=True, is_active=True).first()
            if not default_plan:
                default_plan = Plan.objects.filter(is_free_trial=True, is_active=True).first()

            if default_plan:
                WalletService.assign_plan(str(user.id), str(default_plan.id), reset_to_zero=True)

            login(request, user)
            messages.success(request, 'تم إنشاء الحساب بنجاح وإضافة رصيد البداية! / Account created with initial credits!')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Try username or email
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                user_obj = User.objects.filter(email=username_or_email).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)

            if user:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'بيانات الدخول غير صحيحة / Invalid credentials')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    subscriptions = request.user.subscriptions.all().order_by('-created_at')
    transactions = request.user.wallet_transactions.all().order_by('-created_at')[:20]
    return render(request, 'accounts/profile.html', {
        'subscriptions': subscriptions,
        'transactions': transactions
    })

def switch_language_view(request):
    lang = request.GET.get('lang', 'ar')
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    response = redirect(next_url)
    if lang in ('ar', 'en'):
        request.session['nexmedia_lang'] = lang
        response.set_cookie('nexmedia_lang', lang, max_age=60 * 60 * 24 * 365)
    return response
