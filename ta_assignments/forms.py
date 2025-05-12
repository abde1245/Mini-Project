# forms.py placeholder
# ta_assignments/forms.py
from django import forms
from .models import TACourseAssignment
from users.models import CustomUser
from courses.models import Course

class TACourseAssignmentForm(forms.ModelForm):
    class Meta:
        model = TACourseAssignment
        fields = ['ta', 'course', 'start_date', 'end_date']
        widgets = {
            'ta': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ta'].queryset = CustomUser.objects.filter(role__role_name='Student')
        self.fields['ta'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name or ''} ({obj.username})"
        self.fields['course'].queryset = Course.objects.all()