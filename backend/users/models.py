from django.db import models

class User(models.Model):
    employee_id = models.AutoField(primary_key=True, auto_created=True)
    e_firstname = models.CharField(max_length=150, blank=True, default='')
    e_lastname = models.CharField(max_length=150, blank=True, default='')
    e_email = models.EmailField(blank=True, default='')
    e_phone = models.CharField(max_length=20, blank=True, default='')
    e_password_hash = models.CharField(max_length=255, blank=True, default='')
    is_manager = models.BooleanField(default=False)

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'employee'
        
    def __str__(self):
        return f"{self.employee_id} - {self.e_firstname} {self.e_lastname}"

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True