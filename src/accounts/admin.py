from django.contrib import admin
from .models import Role, User, TokenVersion, TokenHistory

# Register your models here.

admin.site.register([
    Role, User, TokenVersion, TokenHistory
])
