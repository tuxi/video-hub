# video-hub

用户认证使用JWT（json web token）认证方式

### 初始化

- 创建python虚拟环境
```angular2html
mkvirtualenv -p /usr/bin/python3 videohub
```

- 安装依赖
```
pip install -r requirements.txt
```

- 创建数据库
```angular2html
create database videohub charset=utf8;
```
- 生成数据库
python manage.py makemigrations
python manage.py migrate

- 收集静态文件
```
python manage.py collectstatic --noinput
```

### 问题

##### 1. 使用`createsuperuser`创建一个超级用户后，通过xadmin无法登录。但是通过api接口post`/users/`创建的用户可以登录，由于api接口创建的不是管理员，所以无法登录xadmin，但是密码验证是正确的。

这个问题发生在`users`app的`signals.py`中
```angular2html
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user(sender, instance=None, created=False, **kwargs):
    '''
    接收创建用户的信号，将密码改为密文保存到数据库
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    '''
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()
```

这里导致`createsuperuser`创建用户时密码被`pbkdf2_sha256`算法加密了，当我们添加在`signals.py`接收创建用户的信号时使用`set_password`再次对密码进行加密，导致在登录时密码校验是失败的。
所以这里我们不再使用`signals.py`。
解决方法:
不使用signals全局信号量，我们在用户注册的序列化模块(`UserRegisterSerializer`)中重载`create`方法，将注册用户的接口的密码设置为密文。
```angular2html
    def create(self, validated_data):
          #重载父类方法，为了将密码以密文的方式保存到数据库
        users = super(UserRegisterSerializer, self).create(validated_data=validated_data)
        users.set_password(validated_data["password"])
        users.save()
        return users
```

使用django的信号signals，比如当对model进行操作时，django会全局发送一个信号。
我们这里捕获用户的`post_save`信号，在创建用户时同一对其密码进行加密