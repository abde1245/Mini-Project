# users/admin.py

from django import forms # Import forms for ValidationError if needed, though not directly used in this snippet now
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm # Base forms
from .models import CustomUser, Role, Department # Your app's models

# --- STEP 5: SIMPLIFIED CustomUserCreationForm for debugging ---
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Only include the absolute minimum required fields for testing
        # Password fields are handled by UserCreationForm's base.
        # 'email' is in REQUIRED_FIELDS in your CustomUser model.
        # 'role' is the custom NOT NULL field.
        fields = ('username', 'email', 'role')
    
    # No custom clean methods for now, to keep it simple for debugging.

# --- CustomUserChangeForm (for editing existing users - can remain more complete) ---
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta): # Corrected from UserCreationForm.Meta
        model = CustomUser
        # For the change form, you typically want all editable fields
        fields = ('username', 'email', 'first_name', 'last_name',
                'role', 'department', 'employee_code', 'roll_number',
                'major', 'academic_year',
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions') # last_login, date_joined are usually read-only by admin

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # Forms to use for add and change views
    form = CustomUserChangeForm        # Form used for the CHANGE (edit) page
    add_form = CustomUserCreationForm  # Form used for the ADD page (currently simplified)

    # Display in list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role', 'department')
    
    # --- 'fieldsets' are for the CHANGE (edit) page - keep these relatively complete ---
    # This defines the layout of fields on the user *change* page.
    fieldsets = (
        (None, {'fields': ('username', 'password')}), # Password field is handled specially by UserAdmin
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Role and Department'), {'fields': ('role', 'department')}),
        (('Student Specific Info'), {
            'fields': ('roll_number', 'major', 'academic_year'),
            'classes': ('collapse', 'student-fields-class'), # For JS targeting
        }),
        (('Faculty Specific Info'), {
            'fields': ('employee_code',),
            'classes': ('collapse', 'faculty-fields-class'), # For JS targeting
        }),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # --- STEP 5: SIMPLIFIED 'add_fieldsets' for the ADD USER page ---
    # This MUST align with the simplified CustomUserCreationForm.Meta.fields for the add page.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'password2', # These are standard for UserCreationForm
                    'email',      # From our simplified Meta.fields in CustomUserCreationForm
                    'role'),      # From our simplified Meta.fields in CustomUserCreationForm
        }),
        # ALL OTHER FIELDSETS (department, student-specific, faculty-specific, first_name, last_name)
        # ARE TEMPORARILY REMOVED from the ADD USER page layout for this debugging step.
    )
    
    search_fields = ('username', 'first_name', 'last_name', 'email', 'role__name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',) # Makes M2M fields nicer to edit

    # JavaScript for dynamic fields (should still be included, though it might act on fewer elements on the add page now)
    class Media:
        js = (
            'admin/js/jquery.init.js',
            'js/admin_user_form.js', 
        )

    # --- TEMPORARY: Override add_view for debugging form errors ---
    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            form = self.add_form(request.POST, request.FILES)
            print("--- Debug: CustomUserAdmin add_view POST ---")
            if form.is_valid():
                print("Debug: Form IS valid in add_view.")
            else:
                print("Debug: Form IS NOT valid in add_view.")
                print("DEBUG FORM ERRORS START")
                
                # Print structured errors using as_data()
                print(f"Form errors (form.errors.as_data()): {form.errors.as_data()}")
                
                # Print non-field errors more carefully
                non_field_errs = form.non_field_errors()
                if non_field_errs:
                    print("Form non-field errors:")
                    for error in non_field_errs: # non_field_errs is an ErrorList of ValidationErrors
                        if hasattr(error, 'message'):
                            print(f"  - Code: {getattr(error, 'code', 'N/A')}, Message: {error.message}, Params: {getattr(error, 'params', {})}")
                        else:
                            print(f"  - (Raw error string): {error}") # If it's just a string for some reason
                else:
                    print("Form non-field errors: None")

                # Loop through field-specific errors
                print("Field-specific errors:")
                for field_name, error_list in form.errors.items(): # error_list is an ErrorList
                    print(f"  Field: {field_name}")
                    for error_detail in error_list: # Each error_detail is a ValidationError instance
                        # A ValidationError instance always has a 'message' attribute.
                        # It might also have a 'code' and 'params'.
                        print(f"    - Code: {getattr(error_detail, 'code', 'N/A')}, Message: {error_detail.message if not isinstance(error_detail, str) else error_detail}, Params: {getattr(error_detail, 'params', {})}")
                print("DEBUG FORM ERRORS END")
        else:
            print("--- Debug: CustomUserAdmin add_view GET ---")
        
        return super().add_view(request, form_url, extra_context)
    
# Register your other models (Role, Department) so they can be managed in the admin
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)