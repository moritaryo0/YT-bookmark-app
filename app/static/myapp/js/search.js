document.addEventListener('DOMContentLoaded', function() {
    const videoCards = document.querySelectorAll('.video-card');
    const playerModal = document.getElementById('player-modal');
    const playerContent = document.getElementById('player-content');
    const closeBtn = document.getElementById('close-player');

    // 動画プレビュー機能
    function attachVideoCardEvents() {
        document.querySelectorAll('.video-card').forEach(card => {
            card.addEventListener('click', function(e) {
                if (e.target.closest('.video-actions')) return;
                
                const videoId = this.getAttribute('data-video-id');
                if (videoId) {
                    playerContent.innerHTML = `
                        <iframe width="560" height="315" 
                                src="https://www.youtube.com/embed/${videoId}?autoplay=1" 
                                frameborder="0" 
                                allowfullscreen></iframe>
                    `;
                    playerModal.style.display = 'block';
                }
            });
        });
    }

    // ブックマーク機能
    function attachBookmarkEvents() {
        document.querySelectorAll('.bookmark-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                
                const videoId = this.dataset.videoId;
                const videoTitle = this.dataset.videoTitle;
                const videoThumbnail = this.dataset.videoThumbnail;
                const videoPublished = this.dataset.videoPublished;
                const channelId = this.dataset.channelId;
                const channelTitle = this.dataset.channelTitle;
                
                const videoData = {
                    videoId: videoId,
                    title: videoTitle,
                    thumbnail: videoThumbnail,
                    publishedAt: videoPublished || new Date().toISOString(),
                    channelId: channelId,
                    channelTitle: channelTitle
                };
                
                toggleBookmark(videoData, this);
            });
        });
    }

    // グローバル変数でチャンネル情報を保存
    let currentChannelInfo = null;

    // チャンネル検索ボタンのイベントリスナー（修正版）
    function attachChannelSearchEvent() {
        const channelSearchBtn = document.getElementById('channel-search-btn');
        if (channelSearchBtn) {
            // 既存のイベントリスナーを削除
            channelSearchBtn.removeEventListener('click', handleChannelSearch);
            // 新しいイベントリスナーを追加
            channelSearchBtn.addEventListener('click', handleChannelSearch);
        }
    }

    // チャンネル検索のハンドラー関数
    function handleChannelSearch(e) {
        e.preventDefault();
        
        console.log('Channel search button clicked'); // デバッグ用
        
        // グローバル変数から取得を試す
        let channelId = currentChannelInfo?.channelId;
        let channelTitle = currentChannelInfo?.channelTitle;
        
        // グローバル変数が空の場合、data属性から取得
        if (!channelId) {
            channelId = this.dataset.channelId;
            channelTitle = this.dataset.channelTitle;
        }
        
        console.log('Channel ID:', channelId); // デバッグ用
        console.log('Channel Title:', channelTitle); // デバッグ用
        
        if (!channelId) {
            showToast('チャンネル情報が見つかりません', 'error');
            console.error('Channel ID not found in dataset:', this.dataset); // デバッグ用
            return;
        }
        
        // ボタンを無効化してローディング状態にする
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>検索中...';
        
        searchChannelVideosWithForm(channelId, channelTitle)
            .finally(() => {
                // 検索完了後にボタンを元に戻す
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-search me-1"></i>チャンネル動画';
            });
    }

    // 初期化
    attachVideoCardEvents();
    attachBookmarkEvents();
    attachChannelSearchEvent();

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            playerModal.style.display = 'none';
            playerContent.innerHTML = '';
        });
    }

    playerModal?.addEventListener('click', function(e) {
        if (e.target === this) {
            this.style.display = 'none';
            playerContent.innerHTML = '';
        }
    });

    // URL保存フォームの処理
    const urlSaveForm = document.getElementById('url-save-form');
    if (urlSaveForm) {
        urlSaveForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const urlInput = document.getElementById('video-url');
            const saveBtn = document.querySelector('.btn-save');
            const resultDiv = document.getElementById('save-result');
            
            const videoUrl = urlInput.value.trim();
            
            if (!isValidYouTubeUrl(videoUrl)) {
                showToast('有効なYouTube URLを入力してください', 'error');
                return;
            }
            
            // ローディング状態
            saveBtn.disabled = true;
            saveBtn.classList.add('loading');
            resultDiv.style.display = 'none';
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/api/save-video-url/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    url: videoUrl
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('API Response:', data); // デバッグ用
                
                if (data.success || data.video) {
                    // グローバル変数にチャンネル情報を保存
                    currentChannelInfo = {
                        channelId: data.video.channelId,
                        channelTitle: data.video.channelTitle
                    };
                    
                    console.log('Saved channel info:', currentChannelInfo); // デバッグ用
                    
                    // 保存結果を表示（チャンネル情報も設定）
                    showSaveResult({
                        title: data.video.title,
                        channel: data.video.channelTitle,
                        thumbnail: data.video.thumbnail,
                        url: data.video.url,
                        channelId: data.video.channelId,
                        channelTitle: data.video.channelTitle
                    });
                    
                    if (data.success) {
                        showToast(data.message, 'success');
                    } else {
                        showToast(data.message, 'warning');
                    }
                    
                    // フォームをクリア
                    urlInput.value = '';
                    
                    // チャンネル検索ボタンのイベントリスナーを再アタッチ
                    attachChannelSearchEvent();
                } else {
                    showToast(data.error || 'エラーが発生しました', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('通信エラーが発生しました', 'error');
            })
            .finally(() => {
                saveBtn.disabled = false;
                saveBtn.classList.remove('loading');
            });
        });
    }

    // 既存のsearchビューを使ってチャンネル検索する関数
    function searchChannelVideosWithForm(channelId, channelTitle) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        console.log('Starting channel search:', channelId, channelTitle); // デバッグ用
        
        // ローディング表示
        const searchResults = document.getElementById('search-results');
        searchResults.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">読み込み中...</span>
                </div>
                <p class="mt-3">${channelTitle}の動画を検索中...</p>
            </div>
        `;
        
        // FormDataを作成
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', csrfToken);
        formData.append('channel_id', channelId);
        formData.append('keyword', ''); // 空文字
        formData.append('max_results', '10'); // 10件
        
        return fetch('/search/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            console.log('Search response received'); // デバッグ用
            
            // レスポンスのHTMLから動画データを抽出
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // 検索結果セクションを取得
            const newSearchResults = doc.querySelector('.search-results');
            if (newSearchResults) {
                // 現在の検索結果を新しい結果で置き換え
                searchResults.innerHTML = newSearchResults.innerHTML;
                
                // イベントリスナーを再アタッチ
                attachVideoCardEvents();
                attachBookmarkEvents();
                
                // URL保存セクションを非表示にする
                const urlSaveContainer = document.querySelector('.url-save-container');
                if (urlSaveContainer) {
                    urlSaveContainer.style.display = 'none';
                }
                
                // 結果のタイトルを変更
                const resultsTitle = searchResults.querySelector('.results-title');
                if (resultsTitle) {
                    const videoCount = searchResults.querySelectorAll('.video-card').length;
                    resultsTitle.textContent = `${channelTitle}の動画 (${videoCount}件)`;
                }
                
                // 戻るボタンを追加
                const resultsHeader = searchResults.querySelector('.results-header');
                if (resultsHeader && !resultsHeader.querySelector('.btn-back-to-search')) {
                    const backButton = document.createElement('button');
                    backButton.className = 'btn btn-outline-secondary btn-sm btn-back-to-search';
                    backButton.innerHTML = '<i class="fas fa-arrow-left me-1"></i>検索画面に戻る';
                    backButton.onclick = resetSearch;
                    resultsHeader.appendChild(backButton);
                }
                
                showToast(`${channelTitle}の動画を取得しました`, 'success');
            } else {
                console.error('No search results found in response'); // デバッグ用
                searchResults.innerHTML = `
                    <div class="no-results">
                        <div class="no-results-icon">
                            <i class="fas fa-search"></i>
                        </div>
                        <h3>動画が見つかりませんでした</h3>
                        <p>${channelTitle}の動画を取得できませんでした</p>
                    </div>
                `;
                showToast('動画を取得できませんでした', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('通信エラーが発生しました', 'error');
            searchResults.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <h3>エラーが発生しました</h3>
                    <p>動画の取得中にエラーが発生しました</p>
                </div>
            `;
        });
    }

    // 検索画面に戻る関数をグローバルに定義
    window.resetSearch = function() {
        const searchResults = document.getElementById('search-results');
        const urlSaveContainer = document.querySelector('.url-save-container');
        
        searchResults.innerHTML = '';
        if (urlSaveContainer) {
            urlSaveContainer.style.display = 'block';
        }
        showToast('検索画面に戻りました', 'info');
    };
});

function toggleBookmark(videoData, buttonElement) {
    buttonElement.disabled = true;
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/api/toggle-bookmark/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({video: videoData})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('エラー: ' + data.error, 'error');
            return;
        }
        
        const icon = buttonElement.querySelector('i');
        const text = buttonElement.querySelector('.bookmark-text');
        
        if (data.bookmarked) {
            buttonElement.dataset.bookmarked = 'true';
            buttonElement.className = 'btn btn-sm bookmark-btn';
            text.textContent = 'ブックマーク済み';
        } else {
            buttonElement.dataset.bookmarked = 'false';
            buttonElement.className = 'btn btn-sm bookmark-btn';
            text.textContent = 'ブックマーク';
        }
        
        showToast(data.message, 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('通信エラーが発生しました', 'error');
    })
    .finally(() => {
        buttonElement.disabled = false;
    });
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    
    let iconClass = 'fa-check-circle';
    if (type === 'error') iconClass = 'fa-exclamation-circle';
    if (type === 'warning') iconClass = 'fa-exclamation-triangle';
    if (type === 'info') iconClass = 'fa-info-circle';
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas ${iconClass}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

function isValidYouTubeUrl(url) {
    const patterns = [
        /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
        /^https?:\/\/youtu\.be\/[\w-]+/,
        /^https?:\/\/(www\.)?youtube\.com\/embed\/[\w-]+/,
        /^https?:\/\/(www\.)?youtube\.com\/v\/[\w-]+/
    ];
    return patterns.some(pattern => pattern.test(url));
}

function showSaveResult(data) {
    console.log('showSaveResult called with:', data); // デバッグ用
    
    document.getElementById('result-thumbnail').src = data.thumbnail;
    document.getElementById('result-title').textContent = data.title;
    document.getElementById('result-channel').textContent = data.channel;
    document.getElementById('result-link').href = data.url;
    
    // チャンネル検索ボタンにデータを設定
    const channelSearchBtn = document.getElementById('channel-search-btn');
    if (channelSearchBtn && data.channelId && data.channelTitle) {
        console.log('Setting button data:', data.channelId, data.channelTitle); // デバッグ用
        
        channelSearchBtn.setAttribute('data-channel-id', data.channelId);
        channelSearchBtn.setAttribute('data-channel-title', data.channelTitle);
        channelSearchBtn.style.display = 'inline-block'; // ボタンを表示
        
        console.log('Button dataset after setting:', channelSearchBtn.dataset); // デバッグ用
    } else {
        console.error('Button or channel data not found:', channelSearchBtn, data.channelId, data.channelTitle); // デバッグ用
    }
    
    document.getElementById('save-result').style.display = 'block';
} 