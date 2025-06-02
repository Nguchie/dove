from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)  # <-- Add this
    created_at = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class PostSection(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='sections')
    subtitle = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='section_images/', null=True, blank=True)

    def __str__(self):
        return f"Section: {self.subtitle} of {self.post.title}"
