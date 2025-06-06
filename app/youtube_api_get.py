import os
from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    print("Warning: YOUTUBE_API_KEY environment variable is not set. YouTube API functionality will be disabled.")
    YOUTUBE_API_KEY = None
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

##チャンネルIDから最新の動画を取得
def get_latest_video_by_channel_id(channel_id, keyword = None, max_results = None):
    if not YOUTUBE_API_KEY:
        return []
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    channel_response = youtube.channels().list(
        part='contentDetails,snippet',
        id=channel_id,
    ).execute()

    if not channel_response['items']:
        return None

    channel_info = channel_response['items'][0]
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    channel_title = channel_info['snippet']['title']

    # アップロードされた動画を取得（新しい順）
    playlist_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=max_results,

    ).execute()

    videos = []

    for item in playlist_response['items']:
        snippet = item['snippet']
        title = snippet['title']
        if keyword and keyword.lower() not in title.lower():
            continue

        video_data = {
            'videoId': snippet['resourceId']['videoId'],
            'title': title,
            'publishedAt': snippet['publishedAt'],
            'thumbnail': snippet['thumbnails']['high']['url'],
            'channelId': channel_id,
            'channelTitle': channel_title,
        }
        videos.append(video_data)

    return videos

##チャンネルリンクからチャンネルIDを取得
##1.受け取ったチャンネル名からチャンネルIDを取得

def get_channel_id_by_channel_name(channel_name):
    if not YOUTUBE_API_KEY:
        return None
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    response = youtube.search().list(
        part='snippet',
        q=channel_name,
        type='channel',
        maxResults=1,
    ).execute()

    if not response['items']:
        return None

    return response['items'][0]['snippet']['channelId']

##2.受け取ったurlの形式を判定
import re

def parse_channel_url(url):
    # パターン1: /channel/ 形式
    match = re.search(r'youtube\.com/channel/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)

    # パターン2: /@handle 形式（APIで解決）
    match = re.search(r'youtube\.com/@([a-zA-Z0-9_-]+)', url)
    if match:
        handle =  match.group(1)  # → ここでハンドル名からAPI検索へ
        return get_channel_id_by_channel_name(handle)

    # パターン3: /c/カスタムURL形式
    match = re.search(r'youtube\.com/c/([a-zA-Z0-9_-]+)', url)
    if match:
        handle =  match.group(1)  # → これもAPI検索へ
        return get_channel_id_by_channel_name(handle)

    return None