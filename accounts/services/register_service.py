from accounts.models import Account


def create_inactive_account(first_name, last_name, email, phone_number, password):
    username = email.split('@')[0]
    account = Account.objects.create_user(username, email, password, first_name, last_name)
    account.phone_number = phone_number
    account.is_active = False
    account.save()
    return account
