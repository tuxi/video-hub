# -*- coding: utf-8 -*-
# @Time    : 2019/4/5 9:23 PM
# @Author  : alpface
# @Email   : xiaoyuan1314@me.com
# @File    : yunpian.py
# @Software: PyCharm

import requests
import json

class YunPian(object):
    '''
    用于云片发送验证码服务
    '''

    def __init__(self, apikey):
        self.apikey = apikey
        self.single_send_url = 'https://sms.yunpian.com/v2/sms/single_send.json'

    def send_sms(self, code, mobile):
        params = {
            'apikey': self.apikey,
            'mobile': mobile,
            'text': "【杨孝远test】您的验证码是{code}（5分钟内有效，如非本人操作，请忽略本短信）".format(code=code)
        }

        response = requests.post(url=self.single_send_url, data=params)
        res_dict = json.loads(response.text)
        print(res_dict)
        return res_dict

if __name__=='__main__':
    # 测试验证码
    yunpian = YunPian('')
    yunpian.send_sms('2019', '18810181988')