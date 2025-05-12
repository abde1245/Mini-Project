# courses/forms.py
from django import forms
from .models import Course
from users.models import CustomUser # Your user model

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'credits', 'ltp', 'taught_by']
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'ltp': forms.TextInput(attrs={'class': 'form-control'}),
            'taught_by': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Correct the filter to use 'role__name'
        self.fields['taught_by'].queryset = CustomUser.objects.filter(
            role__name='Faculty'  # <--- CORRECTED to role__name
        ).select_related('role') # Good to add select_related
        # Use get_full_name() for better name display if available
        self.fields['taught_by'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username}"