from django.contrib import admin

# Register your models here.
from .models import User,Staff
admin.site.register(User),
admin.site.register(Staff)
