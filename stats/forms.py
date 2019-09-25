from django import forms
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class DateRangeForm(forms.Form):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data.get('end_date')
        if start_date:
            if not end_date:
                end_date = timezone.today()
                if start_date > end_date:
                    raise ValidationError(u'Start date must be in the past.')
            else:
                if start_date > end_date:
                    raise ValidationError(u'Start date must be before end date.')
        else:
            self.cleaned_data['start_date'] = timezone.now().date() - timedelta(days=7)

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        if end_date:
            if end_date > timezone.today():
                raise ValidationError(u'End date must be in the past.')
        else:
            self.cleaned_data['end_date'] = timezone.now().date()
