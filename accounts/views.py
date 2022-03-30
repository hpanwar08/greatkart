import logging
from urllib.parse import urlencode, urlparse

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
from cart.models import Cart, CartItem
from cart.views import _get_session_id

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
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)
        if user:
            # assign anonymous cart to user
            try:
                # get cart items and their variation in current session cart
                cart = Cart.objects.get(cart_id=_get_session_id(request))
                new_cart_items = cart.cart_items.all().prefetch_related('variations')

                new_cart_item_variations = []
                new_cart_items_ids = []
                for new_cart_item in new_cart_items:
                    new_cart_item_variations.append(list(new_cart_item.variations.all()))
                    new_cart_items_ids.append(new_cart_item)

                # get all the items from user's already existing cart
                user_cart_items = CartItem.objects.filter(buyer=user).prefetch_related('variations')
                existing_items = []
                existing_item_ids = []
                for user_cart_item in user_cart_items:
                    existing_items.append(list(user_cart_item.variations.all()))
                    existing_item_ids.append(user_cart_item)

                # find if current cart item is in user's cart, if yes increment else assign user
                for idx, item in enumerate(new_cart_item_variations):
                    if item in existing_items:
                        existing_id = existing_items.index(item)
                        existing_item = existing_item_ids[existing_id]
                        item = new_cart_items_ids[idx]
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item = new_cart_items_ids[idx]
                        item.buyer = user
                        item.save()

            except Cart.DoesNotExist:
                logger.exception('Cart does not exists')

            auth.login(request, user)

            referer_url = request.META.get('HTTP_REFERER')
            query = urlparse(referer_url).query
            logger.info(f"Query {query} {referer_url}")
            query_params = dict(q.split('=') for q in query.split('&') if q)

            if 'next' in query_params:
                return redirect(query_params['next'])

            messages.success(request, 'You are logged in.')
            return redirect('accounts:dashboard')
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


@login_required
def dashboard(request: HttpRequest):
    return render(request, 'accounts/dashboard.html')


def forgot_password(request: HttpRequest):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email__exact=email)

            # send password reset email
            current_site = get_current_site(request)
            email_subject = 'Reset your password'
            email_body = render_to_string('accounts/reset_password_email.html',
                                          {
                                              'user': user,
                                              'domain': current_site,
                                              'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                              'token': default_token_generator.make_token(user)
                                          })

            email_message = EmailMessage(email_subject, email_body, to=[user.email])
            email_message.send()
            messages.success(request, 'Password reset email sent to your email.')
            return redirect('accounts:login')

        except Account.DoesNotExist as e:
            messages.error(request, 'Account does not exist. Please check and type again')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request: HttpRequest, uidb64: str, token: str):
    user = None
    try:
        userid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=userid)
        print(user)
        # return retype password form
    except (ValueError, TypeError, OverflowError, Account.DoesNotExist) as e:
        logger.exception('Error')
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = user.id
        return render(request, 'accounts/reset_password.html')

    messages.error(request, 'Invalid password reset link.')
    return redirect("accounts:login")


def reset_password(request: HttpRequest):
    if request.method == 'POST':
        password = request.POST.get('password')
        password1 = request.POST.get('password1')

        if password == password1:
            uid = request.session.get('uid')
            if uid:
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()

                del request.session['uid']

                messages.success(request, 'Password successfully changed')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid password reset request')
                return redirect('accounts:forgot_password')

        messages.error(request, 'Passwords did not match!')

    return render(request, 'accounts/reset_password.html')
