from django import forms
from django.db.models import Q
from .models import Submission
from users.models import CustomUser, Role # Ensure Role is imported

class StudentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        # 'student' is set in the view.
        # Grading fields are not for students.
        fields = ['assignment', 'submission_file', 'submission_type']
        widgets = {
            'assignment': forms.Select(attrs={'class': 'form-control'}),
            # submission_type uses default select based on model choices
        }

    def __init__(self, *args, **kwargs):
        # user kwarg is passed from the view for context, but not directly used to set a field here
        # as the student field is not part of this form.
        kwargs.pop('user', None)
        assignment_instance = kwargs.pop('assignment_instance', None)

        super().__init__(*args, **kwargs)

        if assignment_instance:
            self.fields['assignment'].initial = assignment_instance
            # Make it non-editable if pre-set, or even hide it
            self.fields['assignment'].disabled = True
            # self.fields['assignment'].widget = forms.HiddenInput() # Optional: to hide completely
        else:
            # If 'assignment' field is active (not disabled/hidden),
            # you might want to filter its queryset based on student's enrollments.
            # This requires passing the student (request.user) to the form and implementing
            # the filtering logic for the 'assignment' field's queryset.
            # For now, assuming 'assignment' is either pre-set or has a general queryset.
            pass

        # Ensure submission_file is required if your model defines it as non-nullable/non-blank
        if not Submission._meta.get_field('submission_file').blank:
            self.fields['submission_file'].required = True


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade_value', 'comments']  # Remove 'graded_by' and 'grading_timestamp'