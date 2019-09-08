from django import forms


class GetCreditsForm(forms.Form):
    no_credits = forms.IntegerField(min_value=1, initial=10)

    class Meta:
        labels = {
            'no_credits': ('Credits to buy')
        }
