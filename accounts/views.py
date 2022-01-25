import logging
from urllib.parse import urlencode

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.forms import RegistrationForm
from accounts.models import Account
from accounts.services import register_service

logger = logging.getLogger(__file__)


def register(request: HttpRequest):
    form = RegistrationForm()

    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            user = register_service.create_inactive_account(first_name, last_name, email, phone_number, password)

            current_site = get_current_site(request)
            email_subject = 'Activate your account'
            email_body = render_to_string('accounts/account_verification_email.html',
                                          {
                                              'user': user,
                                              'domain': current_site,
                                              'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                              'token': default_token_generator.make_token(user)
                                          })

            email_message = EmailMessage(email_subject, email_body, to=[user.email])
            email_message.send()
            logger.info('Verification email sent.')

            base_url = reverse('accounts:login')
            query_string = urlencode({
                'command': 'validation',
                'email': user.email
            })
            url = f"{base_url}?{query_string}"
            return redirect(url)

    context = {
        'form': form
    }

    return render(request, 'accounts/register.html', context)


def login(request: HttpRequest):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        redirect_url = request.GET.get('next')

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


def activate(request: HttpRequest, uidb64: str, token: str):
    user = None
    try:
        userid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=userid)
    except (ValueError, TypeError, OverflowError, Account.DoesNotExist) as e:
        logger.exception('Error')
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is activated')
        logger.info('Account activated')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid verification url!')
        return redirect('accounts:register')
