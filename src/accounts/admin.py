from django.contrib import admin

from .models import Role, User, TokenVersion, TokenHistory

admin.site.register([
    Role, TokenVersion, TokenHistory
])


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'phone',
        'login_count'
    )
