document.addEventListener('DOMContentLoaded', function() {
    const videoCards = document.querySelectorAll('.video-card');
    const playerModal = document.getElementById('player-modal');
    const playerContent = document.getElementById('player-content');
    const closeBtn = document.getElementById('close-player');

    // 動画プレビュー機能
    videoCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // ボタンクリック時は動画プレビューを開かない
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

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            playerModal.style.display = 'none';
            playerContent.innerHTML = '';
        });
    }

    // モーダル背景クリックで閉じる
    playerModal?.addEventListener('click', function(e) {
        if (e.target === this) {
            this.style.display = 'none';
            playerContent.innerHTML = '';
        }
    });

    // ブックマーク機能
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

    // URL保存フォームの処理
    const urlSaveForm = document.getElementById('url-save-form');
    if (urlSaveForm) {
        urlSaveForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const urlInput = document.getElementById('video-url');
            const saveBtn = document.querySelector('.btn-save');
            const resultDiv = document.getElementById('save-result');
            
            const videoUrl = urlInput.value.trim();
            
            // URL形式の簡易バリデーション
            if (!isValidYouTubeUrl(videoUrl)) {
                showToast('有効なYouTube URLを入力してください', 'error');
                return;
            }
            
            // ローディング状態
            saveBtn.disabled = true;
            saveBtn.classList.add('loading');
            resultDiv.style.display = 'none';
            
            // ここでサーバーにURL送信する処理を実装
            // 実際のAPI呼び出しは次のステップで実装
            
            setTimeout(() => {
                saveBtn.disabled = false;
                saveBtn.classList.remove('loading');
                showSaveResult({
                    title: 'サンプル動画タイトル',
                    channel: 'サンプルチャンネル',
                    thumbnail: 'https://via.placeholder.com/320x180',
                    url: videoUrl
                });
            }, 2000);
        });
    }
});

function toggleBookmark(videoData, buttonElement) {
    // ボタンを無効化（連打防止）
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
        
        // ボタンの表示を更新
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
        
        // 成功メッセージを表示
        showToast(data.message, 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('通信エラーが発生しました', 'error');
    })
    .finally(() => {
        // ボタンを再有効化
        buttonElement.disabled = false;
    });
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // アニメーション表示
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // 3秒後に削除
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
        /^https?:\/\/youtu\.be\/[\w-]+/
    ];
    return patterns.some(pattern => pattern.test(url));
}

function showSaveResult(data) {
    document.getElementById('result-thumbnail').src = data.thumbnail;
    document.getElementById('result-title').textContent = data.title;
    document.getElementById('result-channel').textContent = data.channel;
    document.getElementById('result-link').href = data.url;
    document.getElementById('save-result').style.display = 'block';
} 