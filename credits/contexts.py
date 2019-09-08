from credits.models import Wallet


def wallet_contents(request):
    '''
    Adds the user's wallet value to the context if they're logged in.
    '''
    add_context = {}
    if request.user.is_authenticated and not request.user.has_perm('credits.cant_have_wallet'):
        try:
            add_context['wallet_amount'] = request.user.wallet.amount
        except Wallet.DoesNotExist:
            add_context['wallet_amount'] = 0
    return add_context
