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
    
"""class Video(models.Model):
    video_id = models.AutoField(primary_key=True, auto_created=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=100, blank=True, default='')
    url = models.URLField()

    class Meta:
        db_table = 'video'
        """

class Alert(models.Model):
    event_id = models.UUIDField(primary_key=True)
    camera_id = models.CharField(max_length=100)
    employee_name = models.CharField(max_length=255, blank=True, default='')
    trigger_reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)