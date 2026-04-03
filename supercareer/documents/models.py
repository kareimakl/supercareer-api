from django.db import models
from accounts.models import User
from opportunities.models import Job, FreelanceProject


class CV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    content = models.TextField()
    ats_score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)


class Proposal(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('archived', 'Archived'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(FreelanceProject, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Proposal"
        