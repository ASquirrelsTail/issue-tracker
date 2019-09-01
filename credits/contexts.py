from credits.models import Wallet


def wallet_contents(request):
    '''
    Adds the user's wallet value to the context if they're logged in.
    '''
    add_context = {}
    if request.user.is_authenticated:
        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        add_context['wallet_ammount'] = wallet.ammount
    return add_context
