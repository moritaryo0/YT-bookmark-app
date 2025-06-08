from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, YouTube_SearchForm, ChannelInfoForm
from .youtube_api_get import *
from .models import Video, Bookmark
from django.views.decorators.http import require_POST
from datetime import datetime
import json
from django.http import JsonResponse

def index(request):
    return render(request, 'myapp/index.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'アカウントを作成しました！')
            return redirect('my_page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'myapp/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'ログインしました！')
                return redirect('my_page')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

@login_required
def my_page(request):
    recent_bookmarks = Bookmark.objects.filter(
        user=request.user
    ).select_related('video').order_by('-created_at')[:5]
    total_bookmarks = Bookmark.objects.filter(user=request.user).count()
    context = {
        'recent_bookmarks': recent_bookmarks,
        'total_bookmarks': total_bookmarks,
        'total_favorites': total_bookmarks,
    }
    return render(request, 'myapp/my_page.html',context)

@login_required
def search(request):
    """チャンネル情報取得と動画検索の統合処理"""
    videos = []
    channel_data = None
    search_form = YouTube_SearchForm()
    channel_form = ChannelInfoForm()
    
    if request.method == 'POST':
        # チャンネルリンクからchannel_idを検索し、そのチャンネルの動画と情報を返す処理
        if 'channel_input' in request.POST:
            channel_form = ChannelInfoForm(request.POST)
            if channel_form.is_valid():
                channel_input = channel_form.cleaned_data['channel_input']
                keyword = request.POST.get('keyword', '').strip()
                max_results = int(request.POST.get('max_results', 10))
                
                # チャンネルIDを抽出
                channel_id = extract_channel_id_from_url(channel_input)
                if channel_id:
                    # チャンネル情報を取得
                    channel_data = get_channel_details_by_id(channel_id)
                    if channel_data:
                        messages.success(request, 'チャンネル情報を取得しました')
                        try:
                            videos = get_latest_video_by_channel_id(channel_id, keyword, max_results)
                            if videos:
                                messages.success(request, f'動画を{len(videos)}件見つけました')
                            else:
                                messages.info(request, 'このチャンネルに動画が見つかりませんでした')
                        except Exception as e:
                            print(f"Error fetching videos: {e}")
                            messages.warning(request, 'チャンネル情報は取得できましたが、動画の検索でエラーが発生しました')
                    else:
                        messages.error(request, 'チャンネル情報を取得できませんでした')
                else:
                    messages.error(request, '有効なチャンネルIDまたはURLを入力してください')
                
        
        # チャンネルIDが直接指定された場合
        elif 'channel_id' in request.POST:
            search_form = YouTube_SearchForm(request.POST)
            if search_form.is_valid():
                channel_id = search_form.cleaned_data['channel_id']
                keyword = search_form.cleaned_data['keyword']
                max_results = search_form.cleaned_data['max_results']
                if channel_id.strip():
                    # チャンネル情報も同時に取得
                    channel_data = get_channel_details_by_id(channel_id)
                    # 動画を検索
                    videos = get_latest_video_by_channel_id(channel_id, keyword, max_results)
                    if videos:
                        messages.success(request, f'動画を{len(videos)}件見つけました')
                    else:
                        messages.warning(request, '動画が見つかりませんでした')
                else:
                    messages.error(request, 'チャンネルIDを入力してください')
    
    context = {
        'search_form': search_form,
        'channel_form': channel_form,
        'videos': videos,
        'channel_data': channel_data
    }
    return render(request, 'myapp/search.html', context)

@login_required
@require_POST
def toggle_bookmark(request):
    ##ブックマークを追加、削除を行う
    try:
        data = json.loads(request.body)
        video_data = data.get('video')
        if not video_data:
            return JsonResponse({'error': 'エラーが発生しました。'}, status=400)
        video, created = Video.objects.get_or_create(
            video_id = video_data['videoId'],
            defaults={
                'title': video_data['title'],
                'thumbnail_url': video_data['thumbnail'],
                'published_at': datetime.now(),
                'channel_id': video_data.get('channelId',''),
                'channel_title': video_data.get('channelTitle',''),
            }
        )

        bookmark, bookmark_created = Bookmark.objects.get_or_create(
            user = request.user,
            video=video
        )

        if bookmark_created:
            return JsonResponse({
                'bookmarked': True,
                'message': 'ブックマークに追加しました'
            })
        else:
            bookmark.delete()
            return JsonResponse({
                'bookmarked': False,
                'message': 'ブックマークを削除しました'
            })
    except Exception as e:
        return JsonResponse({'error':str(e)},status=500)

@login_required
@require_POST
def remove_bookmark(request,bookmark_id):
    bookmark = get_object_or_404(Bookmark, id=bookmark_id, user=request.user)
    bookmark.delete()
    messages.success(request,'ブックマークを削除しました')
    return redirect('favorites')

@login_required
def favorites(request):
    """お気に入りページを表示する"""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('video')
    search_query = request.GET.get('q','')
    if search_query:
        bookmarks = bookmarks.filter(
            video__title__icontains = search_query
        )
    
    context = {
        'bookmarks': bookmarks,
        'search_query': search_query,
        'total_count': bookmarks.count()
    }
    return render(request, 'myapp/favorites.html', context)

@login_required
@require_POST
def save_video_from_url(request):
    try:
        data = json.loads(request.body)
        video_url = data.get('url','').strip()

        if not video_url:
            return JsonResponse({'error':'urlを指定してください'})
        
        video_id = extract_video_id_from_url(video_url)
        if not video_id:
            return JsonResponse({'error':'無効なURLです'})
        
        video_info = get_video_details_by_id(video_id)
        if not video_info:
            return JsonResponse({'error':'エラーが発生しまsiた'})
        
        video, created = Video.objects.get_or_create(
            video_id=video_info['videoId'],
            defaults={
                'title': video_info['title'],
                'thumbnail_url': video_info['thumbnail'],
                'published_at':datetime.now(),
                'channel_id': video_info['channelId'],
                'channel_title': video_info['channelTitle'],
            }
        )

        bookmark, bookmark_created = Bookmark.objects.get_or_create(
            user=request.user,
            video=video
        )

        video_response = {
            'videoId': video_info['videoId'],
            'title': video_info['title'],
            'thumbnail': video_info['thumbnail'],
            'channelTitle': video_info['channelTitle'],
            'channelId': video_info['channelId'], 
            'url': f"https://www.youtube.com/watch?v={video_info['videoId']}",
        }

        if bookmark_created:
            return JsonResponse({
                'success': True,
                'message': 'ブックマークに追加しました',
                'video': video_response
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'この動画は既にブックマークされています',
                'video': video_response
            })
    except json.JSONDecodeError:
        return JsonResponse({'error': '無効なJSONデータです'}, status=400)
    except Exception as e:
        print(f"Error in save_video_from_url: {e}")
        return JsonResponse({'error': 'サーバーエラーが発生しました'}, status=500)
