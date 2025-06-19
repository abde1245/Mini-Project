# ta_assignments/forms.py
from django import forms
from .models import TACourseAssignment, TAFacultyAssignment
from users.models import CustomUser, Role 
from courses.models import Course

class TACourseAssignmentForm(forms.ModelForm):
    class Meta:
        model = TACourseAssignment
        fields = ['ta', 'course', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ta': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }
        js = ('js/auto_submit_on_ta_change.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import TAFacultyAssignment
        from courses.models import Course
        from users.models import CustomUser
        from django.utils import timezone

        ta_id = None

        # Check if TA is provided in the form data (e.g., after a failed submission)
        if 'ta' in self.data:
            try:
                ta_id = int(self.data.get('ta'))
            except (ValueError, TypeError):
                ta_id = None
        # Check if TA is set in the initial data (e.g., when editing an existing assignment)
        elif self.initial.get('ta'):
            ta_id = self.initial.get('ta').id
        # Check if TA is set in the instance (e.g., when editing an existing assignment)
        elif self.instance and self.instance.ta_id:
            ta_id = self.instance.ta_id

        # Filter courses based on the selected TA
        if ta_id:
            today = timezone.now().date()
            faculty_ids = TAFacultyAssignment.objects.filter(
                ta_id=ta_id,
                end_date__gte=today
            ).values_list('faculty', flat=True)
            self.fields['course'].queryset = Course.objects.filter(taught_by__in=faculty_ids)
        else:
            # Show no courses if no TA is selected
            self.fields['course'].queryset = Course.objects.none()

        # Nice labels
        self.fields['ta'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} (TA)"
        self.fields['course'].label_from_instance = lambda obj: f"{obj.course_code} - {obj.course_name}"

class TAFacultyAssignmentForm(forms.ModelForm):
    class Meta:
        model = TAFacultyAssignment
        fields = ['ta', 'faculty', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ta': forms.Select(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        missing_roles = []
        try:
            ta_role_object = Role.objects.get(name='TA')
            self.fields['ta'].queryset = CustomUser.objects.filter(role=ta_role_object)
        except Role.DoesNotExist:
            missing_roles.append('TA')
            self.fields['ta'].queryset = CustomUser.objects.none()
        except Exception as e:
            self.fields['ta'].queryset = CustomUser.objects.none()
            self.add_error('ta', f"Error fetching TAs: {e}")

        try:
            faculty_role_object = Role.objects.get(name='Faculty')
            self.fields['faculty'].queryset = CustomUser.objects.filter(role=faculty_role_object)
        except Role.DoesNotExist:
            missing_roles.append('Faculty')
            self.fields['faculty'].queryset = CustomUser.objects.none()
        except Exception as e:
            self.fields['faculty'].queryset = CustomUser.objects.none()
            self.add_error('faculty', f"Error fetching Faculty: {e}")
            
        if missing_roles:
            self.add_error(None, f"Cannot process assignment: Critical user role(s) not found: {', '.join(missing_roles)}.")
            
        # Corrected label for TA field
        self.fields['ta'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} (TA)"
        self.fields['faculty'].label_from_instance = lambda obj: f"{obj.get_full_name() or obj.username} (Faculty)"