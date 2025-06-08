import os
import re
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

##受け取ったチャンネル名からチャンネルIDを取得

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

##urlからchannelIdを抽出
def extract_channel_id_from_url(url):
    input_text = url.strip()
    if re.match(r'^UC[a-zA-Z0-9_-]{22}$', input_text):
        return input_text
    patterns = [
        # /channel/形式（直接チャンネルIDが含まれる）
        r'youtube\.com/channel/([a-zA-Z0-9_-]{24})',
        
        # /c/カスタムURL形式
        r'youtube\.com/c/([a-zA-Z0-9_-]+)',
        
        # /@ハンドル形式
        r'youtube\.com/@([a-zA-Z0-9_-]+)',
        
        # /user/ユーザー名形式（古い形式）
        r'youtube\.com/user/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, input_text)
        if match:
            extracted = match.group(1)
            if 'channel/' in pattern:
                return extracted
            return get_channel_id_by_channel_name(extracted)
    
    if not ('http' in input_text.lower() or 'www.' in input_text.lower() or '.com' in input_text.lower()):
        # チャンネル名として検索
        return get_channel_id_by_channel_name(input_text)
    
    return None

def get_channel_details_by_id(channel_id):
    if not YOUTUBE_API_KEY:
        return None
    
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
        
        # channels.list APIを使用してチャンネル情報を取得
        channel_response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()
        
        if not channel_response['items']:
            return None

        channel_item = channel_response['items'][0]
        snippet = channel_item['snippet']
        statistics = channel_item.get('statistics', {})

        channel_icon = snippet.get('thumbnails', {})
        channel_icon_url = (
            channel_icon.get('high', {}).get('url') or
            channel_icon.get('medium', {}).get('url') or
            channel_icon.get('default', {}).get('url') or
            ''
        )
        
        channel_data = {
            'channel_id': channel_id,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'thumbnail': channel_icon_url,
            'subscriber_count': statistics.get('subscriberCount', '0'),
            'video_count': statistics.get('videoCount', '0'),
        }
        return channel_data
        
    except Exception as e:
        print(f"Error in get_channel_details_by_id: {e}")
        return None

##urlからvideoIDを抽出 
def extract_video_id_from_url(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

##videoIDから詳細データを取得する
def get_video_details_by_id(video_id):
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

        response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if not response.get('items'):
            return None
        
        video_item = response['items'][0]
        snippet = video_item['snippet']

        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = (
            thumbnails.get('high', {}).get('url') or
            thumbnails.get('medium', {}).get('url') or
            thumbnails.get('default', {}).get('url') or
            ''
        )
        

        video_data = {
            'videoId': video_id,
            'title': snippet.get('title',''),
            'thumbnail': thumbnail_url,
            'channelId': snippet.get('channelId',''),
            'channelTitle': snippet.get('channelTitle',''),
        }

        return video_data


    except Exception as e:
        print(f"Error:{e}")
        return None
