from django.db import models


class Result(models.Model):
    test_case = models.CharField(max_length=500, unique=True)
    passed = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True, help_text="URL where the test was performed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.test_case}"
