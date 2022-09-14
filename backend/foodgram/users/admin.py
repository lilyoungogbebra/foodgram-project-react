from django.contrib import admin

from users import models


@admin.register(models.CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'username', 'email')
    list_filter = ('username', 'email')


@admin.register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'created_at')
    search_fields = ('user',)
