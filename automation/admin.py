from django.contrib import admin
from django.utils.html import format_html
from automation.models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "test_case",
        "status_badge",
        "comment_preview",
        "created_at",
        "url",
    )
    list_filter = ("passed", "created_at")
    search_fields = ("test_case", "comment")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Test Information",
            {"fields": ("test_case", "passed", "comment")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        color, label = ("#2e7d32", "PASS") if obj.passed else ("#c62828", "FAIL")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:4px;font-weight:bold">{}</span>',
            color,
            label,
        )

    @admin.display(description="Comment")
    def comment_preview(self, obj):
        if not obj.comment:
            return "—"
        return obj.comment[:80] + ("…" if len(obj.comment) > 80 else "")
