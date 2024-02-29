from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings  # Use Django's setting for the AUTH_USER_MODEL



class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        CUSTOMER = "CUSTOMER", 'Customer'
        EMPLOYEE = "EMPLOYEE", 'Employee'
        HOSPITAL="HOSPITAL", 'hospital'
    
    #login_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    #phone = models.CharField(max_length=10, unique=True)  # Unique phone number field
    role = models.CharField(max_length=50, choices=Role.choices)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, unique=True)
    address = models.TextField()
    image = models.ImageField(upload_to="images/customer_images/", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    category_name =models.CharField(max_length=20)
    creation_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.category_name

class Policy(models.Model):
    category= models.ForeignKey('Category', on_delete=models.CASCADE)
    policy_name=models.CharField(max_length=200)
    sum_assurance=models.PositiveIntegerField()
    premium=models.PositiveIntegerField()
    tenure=models.PositiveIntegerField()
    creation_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.policy_name

class PolicyRecord(models.Model):
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    Policy= models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=100,default='Pending')
    creation_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.policy
    
class Question(models.Model):
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    description =models.CharField(max_length=500)
    admin_comment=models.CharField(max_length=200,default='Nothing')
    asked_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.description

#class EmployeeRegistration(models.Model):
    #user = models.OneToOneField(get_user_model(),on_delete=models.CASCADE )
    #first_name = models.CharField(max_length=30)
    #last_name = models.CharField(max_length=30) 
    #phone = models.CharField(max_length=10)
    #address = models.TextField()
    #resume_upload = models.FileField(upload_to='resumes/')
    #def __str__(self):
    #     return str(self.user)


class Office(models.Model):
    officeid = models.CharField(max_length=255, primary_key=True)
    address = models.TextField()
    place = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    pin = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    regdate = models.DateField()

    def __str__(self):
        return self.place


# class Staff(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User", related_name="staff")
#     staffid = models.CharField(max_length=15, unique=True)
#     name = models.CharField(max_length=100)
#     hname = models.CharField(max_length=100, verbose_name="Home Name")
#     place = models.CharField(max_length=100)
#     pin = models.CharField(max_length=6)
#     phone = models.CharField(max_length=10)
#     district = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     dob = models.DateField(verbose_name="Date of Birth")
#     photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = "Staff"
#         verbose_name_plural = "Staff"


# class Agent(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agents")
#     agentid = models.CharField(max_length=15, unique=True)
#     officeid = models.CharField(max_length=15)
#     name = models.CharField(max_length=100)
#     address = models.TextField()  # Changed from addr to address for clarity
#     place = models.CharField(max_length=100)
#     location = models.CharField(max_length=100)
#     pin = models.CharField(max_length=6)
#     phone = models.CharField(max_length=10)
#     gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
#     qualification = models.CharField(max_length=100)  # Changed from Qlfn to qualification for clarity
#     aadhar = models.CharField(max_length=12, unique=True)
#     photo = models.ImageField(upload_to='agent_photos/', blank=True, null=True)
#     registration_date = models.DateField()  # Changed from regdate to registration_date for clarity
#     staff = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, related_name='agents')  # Assuming Staff model is defined as shown previously

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = "Agent"
#         verbose_name_plural = "Agents"