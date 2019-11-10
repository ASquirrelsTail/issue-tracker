from django import forms
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class DateRangeForm(forms.Form):
    '''
    A form to select a daterange. Defaults to 1 week ago to today.
    '''
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def clean_start_date(self):
        '''
        Validates start date. Can't be after end date, or today. Defaults to 7 days ago if not set.
        '''
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data.get('end_date')
        if start_date:
            if not end_date:
                end_date = timezone.now().date()
                if start_date > end_date:
                    raise ValidationError(u'Start date must be in the past.')
            else:
                if start_date > end_date:
                    raise ValidationError(u'Start date must be before end date.')
        else:
            self.cleaned_data['start_date'] = timezone.now().date() - timedelta(days=7)

        return self.cleaned_data['start_date']

    def clean_end_date(self):
        '''
        Validates end date. Cant be after today. Defaults to today.
        '''
        end_date = self.cleaned_data['end_date']
        if end_date:
            if end_date > timezone.now().date():
                raise ValidationError(u'End date must be in the past.')
        else:
            self.cleaned_data['end_date'] = timezone.now().date()

        return self.cleaned_data['end_date']
