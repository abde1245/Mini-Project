# duties/forms.py
from django import forms
from .models import Assignment
from courses.models import Course
from users.models import CustomUser # Use CustomUser
from ta_assignments.models import TACourseAssignment
from django.utils import timezone

class DutyForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'course',
            'title',
            'description',
            'due_date',
            'location',
            'assigned_to'  # <--- CORRECTED FIELD NAME
        ]
        # 'weightage' is in your model, add it here if you want it in the form
        # fields = ['course', 'title', 'description', 'due_date', 'location', 'weightage', 'assigned_to']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}), # Changed from assigned_to_ta_user
            # 'weightage': forms.NumberInput(attrs={'class': 'form-control'}), # If you add weightage
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['due_date'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')

        if user and hasattr(user, 'role') and user.role.role_name == 'Faculty': # Check role_name from Role model
            self.fields['course'].queryset = Course.objects.filter(taught_by_faculty=user)
        else:
            self.fields['course'].queryset = Course.objects.all()

        # Use CustomUser here
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role__role_name='Student').select_related('role') # Match your limit_choices_to in model
        self.fields['assigned_to'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name or ''} ({obj.username})"

        selected_course_id = None
        if self.instance and self.instance.pk and self.instance.course_id:
            selected_course_id = self.instance.course_id
        elif 'course' in self.data:
            try:
                selected_course_id = int(self.data.get('course'))
            except (ValueError, TypeError):
                pass
        elif self.initial.get('course'):
            initial_course = self.initial.get('course')
            selected_course_id = initial_course.id if hasattr(initial_course, 'id') else initial_course

        if selected_course_id:
            try:
                course_instance = Course.objects.get(pk=selected_course_id)
                assigned_ta_ids = TACourseAssignment.objects.filter(
                    course=course_instance,
                ).values_list('ta_user_id', flat=True).distinct()
                # Use CustomUser here
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(id__in=assigned_ta_ids, role__role_name='Student')
            except Course.DoesNotExist:
                self.fields['assigned_to'].queryset = CustomUser.objects.none()
        else:
            self.fields['assigned_to'].queryset = CustomUser.objects.none()


    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get("course")
        assigned_ta = cleaned_data.get("assigned_to") # Changed from assigned_to_ta_user

        if course and assigned_ta:
            is_ta_for_course = TACourseAssignment.objects.filter(
                course=course,
                ta_user=assigned_ta # Assuming ta_user is the field in TA_Course_Assignment linking to CustomUser
            ).exists()
            if not is_ta_for_course:
                self.add_error('assigned_to', f"{assigned_ta.username} is not an active TA for {course.course_code}.")
        return cleaned_data