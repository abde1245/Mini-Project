# models.py placeholder
# departments/models.py
from django.db import models

class Department(models.Model):
    # department_id will be automatically created by Django as 'id' (AutoField, primary_key=True)
    # Django handles sequences for SQLite (default), PostgreSQL, etc., automatically.
    # For Oracle, Django also handles its sequences.
    # So, you don't define department_id explicitly unless you have very specific needs
    # to manage the sequence name directly or use a non-standard PK.

    department_name = models.CharField(max_length=100, unique=True, null=False) # null=False is default for CharField

    def __str__(self):
        return self.department_name

    class Meta:
        # Optional: If you want to match the Oracle table name exactly (Django default would be 'departments_department')
        # db_table = 'Departments'
        verbose_name = "Department"
        verbose_name_plural = "Departments"