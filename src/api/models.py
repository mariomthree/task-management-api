from django.db import models

STATUS_OPTIONS = [
    ("DONE", "Done"),
    ("IN_PROGRESS", "In Progress"),
    ("PENDING", "Pending")
]


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_OPTIONS, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
