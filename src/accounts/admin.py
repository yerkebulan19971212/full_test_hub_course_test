from django.contrib import admin

from .models import Role, User, TokenVersion, TokenHistory, BalanceHistory

admin.site.register([
    Role, TokenVersion, TokenHistory
])


@admin.register(BalanceHistory)
class BalanceHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'balance',
        'student',
        'id',
        'created',
    )
    search_fields = ['student__email', 'student__phone', 'student__username']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'phone',
        'login_count'
    )
    fields = [
        'username',
        'email',
        'phone',
        'role',
        'language',
        'city',
        'school',
        'balance',
        'is_google',
        'user_id',
        'login_count'
    ]
    search_fields = ['email', 'phone', 'id', 'username']
