from django import forms


class GetCreditsForm(forms.Form):
    no_credits = forms.IntegerField(min_value=1, initial=10, label='Number of credits to buy:')
