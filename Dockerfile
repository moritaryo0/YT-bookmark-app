# PythonベースのDockerイメージ
FROM python:3.9

# 作業ディレクトリの作成
WORKDIR /code

# 必要パッケージのインストール（pipだけでOKな場合）
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
