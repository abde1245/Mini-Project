# forms.py placeholder
# duty_tracking/forms.py
from django import forms
from .models import DutyCompletionLog

class MarkDutyCompleteForm(forms.ModelForm):
    class Meta:
        model = DutyCompletionLog
        fields = ['duty', 'status', 'comments']  # fulfilled_by and updated_by are set in view/admin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally hide duty if you want to set it in the view