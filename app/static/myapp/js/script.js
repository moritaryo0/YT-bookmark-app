document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password1');
    const strengthMeter = document.querySelector('.strength-meter-fill');
    const strengthText = document.querySelector('.strength-text strong');

    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let feedback = '';

            // 長さチェック
            if (password.length >= 8) strength += 1;
            
            // 大文字チェック
            if (/[A-Z]/.test(password)) strength += 1;
            
            // 小文字チェック
            if (/[a-z]/.test(password)) strength += 1;
            
            // 数字チェック
            if (/[0-9]/.test(password)) strength += 1;
            
            // 特殊文字チェック
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;

            // 強度の表示を更新
            strengthMeter.setAttribute('data-strength', Math.min(strength, 4));
            
            // 強度のテキストを更新
            switch(strength) {
                case 0:
                    feedback = '弱';
                    break;
                case 1:
                    feedback = '弱';
                    break;
                case 2:
                    feedback = '中';
                    break;
                case 3:
                    feedback = '強';
                    break;
                case 4:
                case 5:
                    feedback = '非常に強';
                    break;
            }
            strengthText.textContent = feedback;
        });
    }

    // パスワード確認の一致チェック
    const password2Input = document.getElementById('password2');
    if (password2Input) {
        password2Input.addEventListener('input', function() {
            const password1 = passwordInput.value;
            const password2 = this.value;
            
            if (password1 !== password2) {
                this.setCustomValidity('パスワードが一致しません');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}); 