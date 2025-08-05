"""
Custom widgets for email_api forms
"""
from django.forms import DateInput, TimeInput


class ChicagoDatePickerInput(DateInput):
    """Custom date picker widget with Chicago timezone support"""
    template_name = 'widgets/chicago_date_picker.html'
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'type': 'date',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class ChicagoTimePickerInput(TimeInput):
    """Custom time picker widget with Chicago timezone support"""
    template_name = 'widgets/chicago_time_picker.html'
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'type': 'time',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
