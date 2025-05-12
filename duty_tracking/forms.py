# forms.py placeholder
# duty_tracking/forms.py
from django import forms
from .models import DutyCompletionLog

class MarkDutyCompleteForm(forms.ModelForm):
    class Meta:
        model = DutyCompletionLog
        # Assignment and TA user will be set in the view
        fields = ['status', 'comments'] 
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional comments...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TAs should primarily mark as 'Completed'. 
        # You might want to restrict choices or set default.
        # self.fields['status'].initial = 'Completed' 