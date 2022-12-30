import os
import hmac
import time
import urllib
import base64
import hashlib
import requests
from jinja2 import Environment, FileSystemLoader
from XTestRunner.config import RunResult

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(BASE_DIR, "html")
env = Environment(loader=FileSystemLoader(HTML_DIR))


class Weinxin:
    """
    SendNail group notification
    help doc:
        https://open.dingtalk.com/document/group/enterprise-created-chatbot
    """

    def __init__(self, access_token, at_mobiles: list = None, is_at_all: bool = False):
        """
        :param access_token:  钉钉机器人的Webhook地址
        :param key: 如果钉钉机器人安全设置了关键字，则需要传入对应的关键字。
        :param app_secret: 如果钉钉机器人安全设置了签名，则需要传入对应的密钥。
        :param at_mobiles: 发送通知钉钉中要@人的手机号列表，如：[137xxx, 188xxx]。
        :param is_at_all: 是否@所有人，默认为False, 设为True则会@所有人。
        success:
                {"errcode":0, "errmsg":"ok"}
            fail:
                {"errcode":错误码, "errmsg":"失败原因"}
        """
        self.url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={access_token}"
        self.at_mobiles = at_mobiles
        self.is_at_all = is_at_all

    @staticmethod
    def _get_notice_content():
        """
        get notice content
        """
        res_text = env.get_template('notice_tmp.md').render(
            title=RunResult.title,
            tester=RunResult.tester,
            start_time=RunResult.start_time,
            end_time=RunResult.end_time,
            duration=RunResult.duration,
            p_number=RunResult.passed,
            pass_rate=RunResult.pass_rate,
            f_number=RunResult.failed,
            failure_rate=RunResult.failure_rate,
            e_number=RunResult.errors,
            error_rate=RunResult.error_rate,
            s_number=RunResult.skipped,
            skip_rate=RunResult.skip_rate,
        )
        return res_text

    @staticmethod
    def _send_message(wx_url: str, data: dict):
        """
        发送微信消息
        :param wx_url: webhooks加密后地址
        :param data: 消息详情
        :return:
        """
        headers = {"Content-Type": "application/json"}
        print(wx_url)
        print(dict(data))
        result = requests.post(wx_url, headers=headers, json=dict(data))
        return result.json()

    def send_text(self, content):
        """
        发送text类型消息
        :return:
        """
        # 推送人手机号码
        if self.at_mobiles is None:
            at_mobiles = []

        if self.is_at_all is True:
            self.at_mobiles.append("@all")

        message = {"msgtype": "text", "text": {"content": content, "mentioned_mobile_list": self.at_mobiles}}
        resp = self._send_message(self.url, message)
        if resp["errcode"] == 0:
            print(" 📧 dingTalk sent successfully!!")
        else:
            print("❌ dingTalk failed to send!!")
            print(resp)
        return resp

    def send_markdown(self, content):
        """
        发送markdown类型的消息
        :param content: markdown格式详情
        :return:
        """
        message = {"msgtype": "markdown", "markdown": {"content": content}}
        resp = self._send_message(self.url, message)
        print(resp)
        if resp["errcode"] == 0:
            print(" 📧 dingTalk sent successfully!!")
        else:
            print("❌ dingTalk failed to send!!")
            print(resp)
        return resp


if __name__ == '__main__':
    weixin = Weinxin(
        access_token="50327a8c-59c3-4be7-bf44-a7ad4ec749b5",
        at_mobiles=[13700000000, 13800000000],
        is_at_all=True,
    )
    weixin.send_text("测试")
    weixin.send_markdown('实时新增用户反馈<font color="warning">132例</font>，请相关同事注意。')
