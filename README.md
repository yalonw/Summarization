![summarization](app_news_summary/static/images/ss_logo.png)

<br>

## 前置作業
```shell
sudo apt-get install python3-pip
pip3 install -r requirements.txt

wget -q https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip
unzip -o chinese_L-12_H-768_A-12.zip
```
 <!-- DEBUG=False -->
```shell
python manage.py collectstatic
```
<br>

## RUN 執行
因為 Tensorflow 和 Keras 的關係，執行 Django 時，要加 `--nothreading --noreload`
```shell
python manage.py runserver --nothreading --noreload
```