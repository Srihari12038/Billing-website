from django.contrib import admin

from .models import AuditLog, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "phone", "remember_me", "created_at"]
    list_filter = ["role", "remember_me"]
    search_fields = ["user__username", "user__email", "phone"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "model_name", "object_id", "user", "ip_address", "created_at"]
    list_filter = ["action", "model_name", "created_at"]
    search_fields = ["action", "model_name", "object_id", "user__username"]
    readonly_fields = ["created_at"]

# Register your models here.
