from django.db import models
from core.models import User


class Gem(models.Model):
    """Artist/Talent profile"""
    CATEGORY_CHOICES = [
        ('singer', 'Singer'),
        ('dancer', 'Dancer'),
        ('musician', 'Musician'),
        ('artist', 'Visual Artist'),
        ('athlete', 'Athlete'),
        ('coach', 'Coach'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gem_profile')
    stage_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    cover_image_url = models.URLField(blank=True)
    profile_image_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.stage_name or self.user.email

    def get_display_name(self):
        return self.stage_name or f"{self.user.firstname} {self.user.lastname}".strip() or self.user.email


class OpenCall(models.Model):
    """Job/gig opportunities posted by owners"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closing', 'Closing Soon'),
        ('closed', 'Closed'),
    ]

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='open_calls')
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=Gem.CATEGORY_CHOICES, default='other')
    city = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    """Artist applying to an open call"""
    open_call = models.ForeignKey(OpenCall, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('open_call', 'applicant')

    def __str__(self):
        return f"{self.applicant.email} → {self.open_call.title}"
