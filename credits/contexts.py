from credits.models import Wallet


def wallet_contents(request):
    '''
    Adds the user's wallet balance to the context if they're logged in.
    '''
    add_context = {}
    if request.user.is_authenticated and not request.user.has_perm('credits.cant_have_wallet'):
        try:
            add_context['wallet_balance'] = request.user.wallet.balance
        except Wallet.DoesNotExist:
            add_context['wallet_balance'] = 0
    return add_context
