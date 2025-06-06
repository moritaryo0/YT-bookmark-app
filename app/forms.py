from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フォームのラベルを日本語化
        self.fields['username'].label = 'ユーザー名'
        self.fields['email'].label = 'メールアドレス'
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認）'
        
        # ヘルプテキストを日本語化
        self.fields['username'].help_text = '150文字以下。文字、数字、@/./+/-/_ のみ使用可能。'
        self.fields['password1'].help_text = '8文字以上で、数字だけのパスワードにはできません。'
        self.fields['password2'].help_text = '確認のため、同じパスワードを入力してください。'
        
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
