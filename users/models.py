from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """"Custom user model with role based access"""

    role_choices = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
    )

    role = models.CharField(max_length=20, choices=role_choices, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_customer(self):
        return self.role == 'customer'
    def is_staff_member(self):
        return self.role == 'staff'
    def is_manager(self):
        return self.role == 'manager'