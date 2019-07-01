# video-hub
搭建一个短视频后台, 原项目[shortVideo](https://github.com/tuxi/shortvideo), 使用Django REST framework 编写 RESTful API, 优化服务新建的项目

用户认证使用JWT（json web token）认证方式

### 安装视频编解码依赖

- ffmpeg 安装ffmpeg
```
sudo add-apt-repository ppa:kirillshkrogalev/ffmpeg-next
sudo apt-get update
sudo apt-get install ffmpeg
```

- mediainfo 安装mediainfo
```
sudo add-apt-repository ppa:shiki/mediainfo
sudo apt-get update
sudo apt-get install mediainfo mediainfo-gui
```

mediainfo-gui即可启动

- redis-server 安装redis-server
```
sudo apt-get install -y python-software-properties
sudo apt-get install software-properties-common
sudo add-apt-repository  ppa:chris-lea/redis-server
sudo apt-get update
sudo apt-get install -y redis-server
```

### 初始化 Django project

- 创建python虚拟环境
```angular2html
mkvirtualenv -p /usr/bin/python3 videohub
```

- 安装Django project 依赖
```
pip install -r requirements.txt
```

- 创建数据库
```angular2html
create database videohub charset=utf8;
```
- 生成数据库
```
# 1. 创建更改的文件
python manage.py makemigrations
# 2. 将生成的py文件应用到数据库
python manage.py migrate
```

- 创建管理员
```
python manage.py createsuperuser
```

- 收集静态文件
```
python manage.py collectstatic --noinput
```

- 运行项目
```
python manage.py runserver 8000
```

- 清空数据库
```
python manage.py flush
```
此命令会询问是 `yes` 还是 `no`, 选择 `yes` 会把数据全部清空掉，只留下空表。

