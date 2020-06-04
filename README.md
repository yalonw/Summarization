![summarization](app_news_summary/static/images/ss_logo.png)

<br>

# 開發版
1. 安裝 python 套件
1. 下載及解壓縮 bert_models 資料
1. 因為 Tensorflow 和 Keras 的關係，執行 Django 時，要加 `--nothreading --noreload`
```
pip install -r requirements.txt

wget -q https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip
unzip -o chinese_L-12_H-768_A-12.zip

python manage.py runserver --nothreading --noreload
```

<br>

# 部署版

1. 更新部署環境 ── Linux (VM)
   - 更新套件資料庫
   - 更改時區
   - 安裝解壓縮工具
   - 安裝 pip3
```
sudo apt-get update
sudo timedatectl set-timezone Asia/Taipei
sudo apt-get install unzip
sudo apt-get install python3-pip
```

2. 下載及安裝所需套件
   - 下載準備部署的專案 
   - 安裝 python 套件
   - 下載及解壓縮 bert_models 資料
```
git clone https://github.com/yalonw/Summarization.git

cd Summarization
pip3 install -r requirements.txt

wget -q https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip
unzip -o chinese_L-12_H-768_A-12.zip
```

3. 將靜態資源打包，方便部署專案
```
python manage.py collectstatic
```

4. 使用 NGINX + uWSGI 做為 Web Server ( 前置設定 )   
   - 安裝 uWSGI 和 NGINX
   - 複製 NGINX 參數檔 ( my_project.conf ) 到 sites-available，再以 symbolic link 方式放到 sites-enabled
   - 設定 Unix socket ( 不使用 TCP port )
```
pip3 install uwsgi
sudo apt-get install nginx

sudo cp config/my_project.conf /etc/nginx/sites-available/my_project.conf
sudo ln -s /etc/nginx/sites-available/my_project.conf /etc/nginx/sites-enabled/my_project.conf

uwsgi --socket socket.sock --module project.wsgi --chmod-socket=666
```

5. 使用 NGINX + uWSGI 做為 Web Server ( 啟用執行 ) 
   - 執行 uWSGI
   - 重新載入 NGINX
```
uwsgi --ini config/uwsgi.ini
nginx -s reload
```

6. 查看 log 紀錄
```
tail -f config/uwsgi.log
tail -f config/nginx_error.log
tail -f config/nginx_access.log
```

> 其他參考資料：https://uwsgi.readthedocs.io/en/latest/tutorials/Django_and_nginx.html