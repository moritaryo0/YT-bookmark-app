from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com(任意)'
        })
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスはすでに使用済みです。')
        
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フォームのラベルを日本語化
        self.fields['username'].label = 'ユーザー名'
        self.fields['email'].label = 'メールアドレス(任意)'
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認）'
        
        # ヘルプテキストを日本語化
        self.fields['username'].help_text = '150文字以下。文字、数字、@/./+/-/_ のみ使用可能。'
        self.fields['password1'].help_text = '8文字以上で、数字だけのパスワードにはできません。'
        self.fields['password2'].help_text = '確認のため、同じパスワードを入力してください。'
        self.fields['email'].help_text = 'パスワードリセットで使用します。空欄でも登録可能。'
        
        # 各フィールドにBootstrapクラスを適用
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label,
                    'autocomplete': 'new-password'
                })

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フォームのラベルを日本語化
        self.fields['username'].label = 'ユーザー名'
        self.fields['password'].label = 'パスワード'
        
        # 各フィールドにBootstrapクラスを適用
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label,
                    'autocomplete': 'current-password'
                })

class YouTube_SearchForm(forms.Form):
    channel_id = forms.CharField(
        label='YouTubeチャンネルID',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'YouTubeチャンネルIDを入力'
        })
    )
    keyword = forms.CharField(
        label='キーワード',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'キーワードを入力'
        })
    )
    max_results = forms.IntegerField(
        label='最大取得数',
        min_value=1,
        max_value=50,
        initial=10,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1-255の間で指定'
        })
    )

class ChannelInfoForm(forms.Form):
    """チャンネル情報取得用フォーム"""
    channel_input = forms.CharField(
        label='チャンネルIDまたはURL',
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'UC_x5XG1OV2P6uZZ5FSM9Ttw または https://www.youtube.com/@GoogleDevelopers'
        })
    )

class IntegratedChannelSearchForm(forms.Form):
    """統合されたチャンネル検索フォーム"""
    channel_input = forms.CharField(
        label='チャンネルIDまたはURL',
        max_length=500,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'UC_x5XG1OV2P6uZZ5FSM9Ttw または https://www.youtube.com/@GoogleDevelopers'
        })
    )
    keyword = forms.CharField(
        label='キーワード（オプション）',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '特定のキーワードで絞り込み'
        })
    )
    max_results = forms.IntegerField(
        label='最大取得数',
        min_value=1,
        max_value=50,
        initial=10,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1-50の間で指定'
        })
    )
