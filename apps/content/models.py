from django.db import models
from apps.core.models import BaseModel

class BlogPost(BaseModel):
    slug = models.SlugField(max_length=255, unique=True)
    category = models.CharField(max_length=100, default='general')
    title_en = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255)
    content_en = models.TextField()
    content_ar = models.TextField()
    media_url = models.CharField(max_length=500, blank=True, default='')
    media_type = models.CharField(max_length=50, blank=True, default='')
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title_ar} | {self.title_en}"

class CustomPage(BaseModel):
    slug = models.SlugField(max_length=100, unique=True)
    title_en = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255)
    content_en = models.TextField()
    content_ar = models.TextField()
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.slug}: {self.title_ar}"
