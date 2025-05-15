# duties/forms.py
from django import forms
from .models import Assignment
from courses.models import Course
from users.models import CustomUser, Role # Use CustomUser and Role
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
            'assigned_to'
        ]
        # 'weightage' is in your model, add it here if you want it in the form
        # fields = ['course', 'title', 'description', 'due_date', 'location', 'weightage', 'assigned_to']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            # 'weightage': forms.NumberInput(attrs={'class': 'form-control'}), # If you add weightage
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['due_date'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')

        # --- CORRECTIONS HERE ---
        # 1. Use 'user.role.name' to check the role
        # 2. Filter courses using 'taught_by'
        if user and hasattr(user, 'role') and user.role and user.role.name == 'Faculty': # Check role.name
            self.fields['course'].queryset = Course.objects.filter(taught_by=user) # Use 'taught_by'
        else:
            # Consider if non-faculty should see all courses or none in this form context
            self.fields['course'].queryset = Course.objects.all() # Or .none() ?

        # 3. Filter TAs using 'role__name'
        # Ensure 'Student' is the correct role name for TAs in your Role model
        ta_role_object = Role.objects.get(name='TA') # Use Role to get TA role object
        ta_queryset = CustomUser.objects.filter(role=ta_role_object).select_related('role') # Use role__name
        self.fields['assigned_to'].queryset = ta_queryset
        self.fields['assigned_to'].label_from_instance = lambda obj: f"{obj.first_name or ''} {obj.last_name or ''} ({obj.username})"

        # --- Logic to filter TAs based on selected course ---
        selected_course_id = None
        # Try getting course from instance (editing)
        if self.instance and self.instance.pk and self.instance.course_id:
            selected_course_id = self.instance.course_id
        # Try getting course from submitted data (POST request)
        elif 'course' in self.data:
            try:
                selected_course_id = int(self.data.get('course'))
            except (ValueError, TypeError):
                pass
        # Try getting course from initial data (GET request with initial values)
        elif self.initial.get('course'):
            initial_course = self.initial.get('course')
            # Handle both object and ID initial data
            selected_course_id = initial_course.id if hasattr(initial_course, 'id') else initial_course

        if selected_course_id:
            try:
                # Find TAs specifically assigned to this course via TACourseAssignment model
                assigned_ta_ids = TACourseAssignment.objects.filter(
                    course_id=selected_course_id,
                    # Add date range checks if your TA assignments have start/end dates
                    # start_date__lte=timezone.now(),
                    # end_date__gte=timezone.now(),
                ).values_list('ta_user_id', flat=True).distinct()

                # Filter the initial TA queryset to only those assigned to the selected course
                # 4. Use 'role__name' again here
                self.fields['assigned_to'].queryset = ta_queryset.filter(id__in=assigned_ta_ids, role=ta_role_object)
            except Exception as e: # Catch potential errors during lookup
                print(f"Error filtering TAs for course {selected_course_id}: {e}")
                self.fields['assigned_to'].queryset = CustomUser.objects.none()
        else:
            # If no course is selected, show no TAs initially (or all TAs if preferred)
            self.fields['assigned_to'].queryset = CustomUser.objects.none()
            # Or self.fields['assigned_to'].queryset = ta_queryset # Show all TAs initially

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get("course")
        assigned_ta = cleaned_data.get("assigned_to")

        if course and assigned_ta:
            # Verify if the selected TA is actually assigned to the selected Course
            # Assumes 'ta_user' is the FK field in TACourseAssignment linking to CustomUser
            is_ta_for_course = TACourseAssignment.objects.filter(
                course=course,
                ta_user=assigned_ta
                # Add date checks here too if relevant
            ).exists()
            if not is_ta_for_course:
                self.add_error('assigned_to', f"{assigned_ta.username} is not an active TA for {course.course_code}.")
        return cleaned_data