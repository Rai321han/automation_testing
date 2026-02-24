from django.contrib import admin
from .models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "test_case_name", "passed", "created_at")
    list_filter = ("passed", "created_at")
    search_fields = ("test_case_name", "comment")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Test Information", {"fields": ("test_case_name", "passed", "comment")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
