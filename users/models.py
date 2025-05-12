# models.py placeholder
# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# 1. Role Model (as you have it)
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Student, Faculty, Admin

    def __str__(self):
        return self.name

# 2. Department Model (as you have it)
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# 3. Custom User Manager
class CustomUserManager(BaseUserManager):
    def _validate_role(self, role_identifier):
        print(f"--- Debug: _validate_role CALLED with identifier (type: {type(role_identifier)}): '{role_identifier}'")
        if isinstance(role_identifier, Role):
            print(f"Debug: Identifier is already a Role instance: {role_identifier}")
            return role_identifier
        try:
            role_pk = int(role_identifier)
            print(f"Debug: Identifier parsed as int: {role_pk}. Querying Role by PK.")
            role_obj = Role.objects.get(pk=role_pk)
            print(f"Debug: Role found by PK: {role_obj}")
            return role_obj
        except (ValueError, TypeError):
            if isinstance(role_identifier, str):
                print(f"Debug: Identifier is a string: '{role_identifier}'. Querying Role by name (iexact).")
                try:
                    role_obj = Role.objects.get(name__iexact=role_identifier)
                    print(f"Debug: Role found by name: {role_obj}")
                    return role_obj
                except Role.DoesNotExist:
                    print(f"Debug: !!! Role with name '{role_identifier}' does not exist.")
                    raise ValueError(_(f'Role with name "{role_identifier}" does not exist.'))
            else:
                print(f"Debug: !!! Invalid role identifier type: {type(role_identifier)}")
                raise ValueError(_('Invalid role identifier provided. Must be a Role instance, ID, or name.'))
        except Role.DoesNotExist:
            print(f"Debug: !!! Role with ID '{role_identifier}' does not exist.")
            raise ValueError(_(f'Role with ID "{role_identifier}" does not exist.'))


    def create_user(self, username, password=None, role=None, **extra_fields):
        print(f"--- Debug: CustomUserManager.create_user CALLED ---")
        print(f"Debug: Received username: '{username}'")
        print(f"Debug: Password provided: {'Yes' if password else 'No'}")
        print(f"Debug: Role received (type: {type(role)}): '{role}'") # Crucial: what is its type and value?
        print(f"Debug: Extra fields received: {extra_fields}")

        if not username:
            print("Debug: Username validation failed (empty).")
            raise ValueError(_('The Username must be set'))
        if not role:
            print(f"Debug: Role validation failed (empty/None). Role was: {role}") # Crucial
            raise ValueError(_('The Role must be set for a user'))

        print(f"Debug: Attempting to validate role: '{role}'")
        try:
            role_instance = self._validate_role(role)
            print(f"Debug: Role validated successfully: {role_instance} (ID: {role_instance.id})")
        except ValueError as e:
            print(f"Debug: !!! ERROR in _validate_role: {e}")
            raise e # Re-raise to see it as the error

        email = extra_fields.get('email')
        if email:
            email = self.normalize_email(email)
            extra_fields['email'] = email
            print(f"Debug: Email normalized: {email}")
        else:
            print(f"Debug: No email in extra_fields.")
            # If email is truly required for user creation by your logic beyond REQUIRED_FIELDS for createsuperuser
            # if not email and 'email' not in self.model.REQUIRED_FIELDS: # Adjust logic if email is always needed
            #     raise ValueError("Email is required for user creation.")


        # Ensure 'email' from extra_fields is passed to the model if it's a model field
        # and not already handled by AbstractUser if it's the USERNAME_FIELD.
        # Your CustomUser inherits email from AbstractUser.
        # UserCreationForm's save method usually passes 'email' in extra_fields if present in the form.

        print(f"Debug: Preparing to create model instance with username='{username}', role_id={role_instance.id}, extra_fields={extra_fields}")
        user = self.model(username=username, role=role_instance, **extra_fields)
        user.set_password(password)

        print(f"Debug: Attempting to save user: {username}")
        try:
            user.save(using=self._db)
            print(f"Debug: User '{username}' saved successfully to database.")
        except Exception as e: # Catch any exception during save
            print(f"Debug: !!! DATABASE SAVE FAILED for user '{username}': {e}")
            print(f"Debug: User fields were: username={user.username}, email={user.email}, role_id={user.role_id}")
            # Check other fields that have unique constraints
            print(f"Debug: roll_number={getattr(user, 'roll_number', 'N/A')}, employee_code={getattr(user, 'employee_code', 'N/A')}")
            raise e # Re-raise the exception to see it clearly
        
        print(f"--- Debug: CustomUserManager.create_user COMPLETED for '{username}' ---")
        return user


    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Ensure superuser is active

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        # Get or create the 'Admin' role (or your preferred superuser role name)
        # This ensures the role exists before trying to assign it.
        admin_role_name = 'Admin' # Define your admin role name here
        try:
            # Use get_or_create to create it if it doesn't exist.
            # This is crucial: the Role table must exist (run migrations for Role first)
            admin_role, created = Role.objects.get_or_create(name=admin_role_name)
            if created:
                print(f"INFO: Created '{admin_role_name}' role as it did not exist.")
        except Exception as e:
            # This might happen if Role table doesn't exist yet, or other DB issues.
            raise ValueError(
                f"Could not get or create the '{admin_role_name}' role. "
                f"Ensure migrations for the Role model have been run. Original error: {e}"
            )

        # Call create_user with the admin_role instance
        return self.create_user(username, password, role=admin_role, **extra_fields)

# 4. Custom User Model (Updated)
class CustomUser(AbstractUser):
    # 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined'
    # are inherited from AbstractUser.
    # 'password' is also handled by AbstractUser.

    # Your custom fields:
    role = models.ForeignKey(Role, on_delete=models.CASCADE) # Stays as NOT NULL, CASCADE is fine if appropriate
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    employee_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    roll_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    major = models.CharField(max_length=100, null=True, blank=True)
    academic_year = models.CharField(max_length=50, null=True, blank=True)

    # is_active = models.BooleanField(default=True) # This is inherited from AbstractUser, redundant

    # Tell Django to use your custom manager
    objects = CustomUserManager()

    # USERNAME_FIELD defines which field is used for login. Default is 'username'.
    # If you wanted to use email for login:
    # USERNAME_FIELD = 'email'
    # email = models.EmailField(_('email address'), unique=True) # Make email unique if it's USERNAME_FIELD
    # username = None # Remove the username field if email is the USERNAME_FIELD

    # REQUIRED_FIELDS are fields prompted for when creating a user via createsuperuser,
    # IN ADDITION to USERNAME_FIELD and password.
    # 'role' should NOT be here as our manager handles it.
    # 'email' is a common one if it's not the USERNAME_FIELD but is required.
    REQUIRED_FIELDS = ['email'] # Assuming you want to be prompted for email

    # To avoid clashes with the default User model's reverse relations if AUTH_USER_MODEL is set.
    # This is good practice for any Custom User Model inheriting from AbstractUser.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_groups", # Use a unique related_name
        related_query_name="customuser_group",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_permissions", # Use a unique related_name
        related_query_name="customuser_permission",
    )

    def __str__(self):
        return self.username # Or self.email if you set email as USERNAME_FIELD