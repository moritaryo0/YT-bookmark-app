from .models import Video, Bookmark
from django.contrib.auth.models import User
from datetime import datetime

new_video = Video.objects.create(
    video_id = 'P4rVZi36D-c',
    title = 'ミサイドもん#2【ずんだもん】',
    channel_id = 'UC_E1wWVfcVeGGXABOLPjy0g',
    thumbnail_url = 'https://i.ytimg.com/vi/P4rVZi36D-c/hqdefault.jpg',
    published_at = datetime.now(),
)
