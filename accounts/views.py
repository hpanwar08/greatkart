from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render, redirect

from accounts.forms import RegistrationForm
from accounts.models import Account


def register(request: HttpRequest):
    form = RegistrationForm()

    if request.method == 'POST':
        print('post', request.POST)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print(form.data)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            username = email.split('@')[0]
            account = Account.objects.create_user(username, email, password, first_name, last_name)
            account.phone_number = phone_number
            account.save()

            messages.success(request, 'Registration completed.')
            return redirect('accounts:register')

    context = {
        'form': form
    }

    return render(request, 'accounts/register.html', context)


def login(request: HttpRequest):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)
        if user:
            auth.login(request, user)
            return redirect('store:store')
        else:
            messages.error(request, "Incorrect username or password")
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')


@login_required
def logout(request: HttpRequest):
    auth.logout(request)
    messages.success(request, 'You are logged out. Login again!')
    return redirect('accounts:login')
