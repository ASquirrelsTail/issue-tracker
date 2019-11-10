from django.test import TestCase
from datetime import date, timedelta
from stats.forms import DateRangeForm


class DateRangeFormTestCase(TestCase):
    '''
    Class for testing DateRangeForm.
    '''
    def test_empty_form_returns_this_week(self):
        '''
        An empty form returns valid with a start date of one week ago, and an end date of today.
        '''
        form = DateRangeForm({})
        self.assertTrue(form.is_valid())
        self.assertEqual(date.today() - timedelta(days=7), form.cleaned_data['start_date'])
        self.assertEqual(date.today(), form.cleaned_data['end_date'])

    def test_no_end_date_defaults_to_today(self):
        '''
        An empty end date should default to today.
        '''
        form = DateRangeForm({'start_date': '2019-01-01'})
        self.assertTrue(form.is_valid())
        self.assertEqual(date.today(), form.cleaned_data['end_date'])

    def test_no_start_date_defaults_to_one_week_before_end_date(self):
        '''
        An empty start date should default to one week before the end date.
        '''
        form = DateRangeForm({'end_date': '2019-01-01'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['end_date'] - timedelta(days=7), form.cleaned_data['start_date'])

    def test_end_date_must_be_in_the_past(self):
        '''
        The end date must be in the past for validation to pass.
        '''
        form = DateRangeForm({'end_date': '2099-01-01'})
        self.assertFalse(form.is_valid())

    def test_start_date_must_be_in_the_past_and_before_end_date(self):
        '''
        The start date must be in the past and before the end date for validation to pass.
        '''
        form = DateRangeForm({'start_date': '2099-01-01'})
        self.assertFalse(form.is_valid())

        form = DateRangeForm({'start_date': '2019-01-05', 'end_date': '2019-01-01'})
        self.assertFalse(form.is_valid())

    def test_start_date_can_be_end_date(self):
        '''
        The start date and the end date can be the same.
        '''
        form = DateRangeForm({'start_date': '2019-01-01', 'end_date': '2019-01-01'})
        self.assertTrue(form.is_valid())
