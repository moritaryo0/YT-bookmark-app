from django.db import models
from django.contrib.auth.models import User, BaseUserManager

class Video(models.Model):
    video_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    channel_id = models.CharField(max_length=200)
    channel_title = models.CharField(max_length=200, blank=True, default='')
    thumbnail_url = models.URLField()
    published_at = models.DateTimeField()

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
    
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.video.title}"