from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
        'placeholder': '••••••••'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
        'placeholder': '••••••••'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'country']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
                'placeholder': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
                'placeholder': 'user@example.com'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
                'placeholder': 'Country'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'كلمات المرور غير متطابقة / Passwords do not match')
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
        'placeholder': 'username or email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm',
        'placeholder': '••••••••'
    }))
