from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Register your models here.
# admin.site.register(model_or_iterable=models.User, admin_class=BaseUserAdmin)
# if you don't add the BaseUserAdmin password will malfunction


@admin.register(User)  # When I use User directly, it doesn't work. I don't know why
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
        }),
    )

