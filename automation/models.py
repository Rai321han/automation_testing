from django.db import models


class Result(models.Model):
    """Model to store test case results"""

    test_case_name = models.CharField(max_length=255, unique=True)
    passed = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Test Result"
        verbose_name_plural = "Test Results"

    def __str__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"{self.test_case_name} - {status}"
