# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property # For efficient property access
from departments.models import Department  # <-- Use this import

# 1. Role Model
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Student, Faculty, Admin

    def __str__(self):
        return self.name

# 3. Custom User Manager
class CustomUserManager(BaseUserManager):
    def _validate_role(self, role_identifier):
        # print(f"--- Debug: _validate_role CALLED with identifier (type: {type(role_identifier)}): '{role_identifier}'")
        if isinstance(role_identifier, Role):
            # print(f"Debug: Identifier is already a Role instance: {role_identifier}")
            return role_identifier
        try:
            role_pk = int(role_identifier)
            # print(f"Debug: Identifier parsed as int: {role_pk}. Querying Role by PK.")
            role_obj = Role.objects.get(pk=role_pk)
            # print(f"Debug: Role found by PK: {role_obj}")
            return role_obj
        except (ValueError, TypeError):
            if isinstance(role_identifier, str):
                # print(f"Debug: Identifier is a string: '{role_identifier}'. Querying Role by name (iexact).")
                try:
                    role_obj = Role.objects.get(name__iexact=role_identifier)
                    # print(f"Debug: Role found by name: {role_obj}")
                    return role_obj
                except Role.DoesNotExist:
                    # print(f"Debug: !!! Role with name '{role_identifier}' does not exist.")
                    raise ValueError(_(f'Role with name "{role_identifier}" does not exist.'))
            else:
                # print(f"Debug: !!! Invalid role identifier type: {type(role_identifier)}")
                raise ValueError(_('Invalid role identifier provided. Must be a Role instance, ID, or name.'))
        except Role.DoesNotExist:
            # print(f"Debug: !!! Role with ID '{role_identifier}' does not exist (after int conversion).")
            raise ValueError(_(f'Role with ID "{role_identifier}" does not exist.'))


    def create_user(self, username, password=None, role=None, **extra_fields):
        # print(f"--- Debug: CustomUserManager.create_user CALLED ---")
        # ... (rest of your create_user method, keep it as is)
        if not username:
            raise ValueError(_('The Username must be set'))

        effective_role_value = role
        if effective_role_value is None:
            effective_role_value = extra_fields.pop('role', None)
            if effective_role_value is None:
                raise ValueError(_('The Role must be set for a user.'))
        else:
            extra_fields.pop('role', None)
        
        try:
            role_instance = self._validate_role(effective_role_value)
        except ValueError as e:
            raise e

        email = extra_fields.get('email')
        if email:
            email = self.normalize_email(email)
            extra_fields['email'] = email

        user = self.model(username=username, role=role_instance, **extra_fields)
        user.set_password(password)
        
        try:
            user.save(using=self._db)
        except Exception as e:
            # print(f"Debug: !!! DATABASE SAVE FAILED for user '{username}': {e}")
            # ... (your error handling)
            raise e
        
        # print(f"--- Debug: CustomUserManager.create_user COMPLETED for '{username}' ---")
        return user


    def create_superuser(self, username, password=None, **extra_fields):
        # print(f"--- Debug: CustomUserManager.create_superuser CALLED for '{username}' ---")
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        admin_role_name = 'Admin'
        try:
            admin_role, created = Role.objects.get_or_create(name=admin_role_name)
            if created:
                print(f"INFO: Created '{admin_role_name}' role as it did not exist during createsuperuser.")
        except Exception as e:
            # print(f"Debug: !!! ERROR getting/creating '{admin_role_name}' role for superuser: {e}")
            raise ValueError(
                f"Could not get or create the '{admin_role_name}' role. "
                f"Ensure migrations for the Role model have been run and the database is accessible. Original error: {e}"
            )
        return self.create_user(username, password, role=admin_role, **extra_fields)

# 4. Custom User Model
class CustomUser(AbstractUser):
    # Ensure 'role' cannot be null. It should be enforced at the DB level by migrations.
    # If you previously had `null=True` and `blank=True` on role,
    # ensure new users always get a role and existing users have one.
    role = models.ForeignKey(Role, on_delete=models.CASCADE, help_text="User's role in the system") 
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    employee_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    roll_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    major = models.CharField(max_length=100, null=True, blank=True)
    academic_year = models.CharField(max_length=50, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] 

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_groups",
        related_query_name="customuser_group",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_permissions",
        related_query_name="customuser_permission",
    )

    def __str__(self):
        base_display = self.get_full_name() if self.first_name else self.username
        # Ensure role is loaded to prevent extra queries if already fetched with select_related
        if hasattr(self, 'role') and self.role:
            return f"{base_display} ({self.role.name})"
        return f"{base_display} (No role assigned)"

    # --- Helper properties for role checking ---
    @cached_property # Use cached_property for efficiency
    def is_admin(self):
        # A superuser is also considered an admin for dashboard purposes
        if self.is_superuser:
            return True
        # Check if self.role is not None before accessing its name
        return self.role is not None and self.role.name == 'Admin'

    @cached_property
    def is_faculty(self):
        return self.role is not None and self.role.name == 'Faculty'

    @cached_property
    def is_student(self):
        # TAs are considered students for their primary role
        return self.role is not None and self.role.name == 'Student'
    
    @cached_property
    def is_student(self):
        return self.role is not None and self.role.name == 'Student'

    @cached_property
    def is_ta(self):
        return self.role is not None and self.role.name == 'TA'