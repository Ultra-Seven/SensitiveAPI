import csv
import json

import pandas as pd
import requests


class SensitiveApi():
    def __int__(self, path):
        print("")


class LCMX(SensitiveApi):
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.url = "https://lcmx-green.mobage.cn"
        self.path = "text/scan3rd"
        self.header = {"Accept": "application/json",
                       "Content-Type": "application/json; charset = utf-8"}
        print("")

    def run_apis(self):
        for text in self.data["文本内容"]:
            requests.post(f"{self.url}/{self.path}", data=myobj, timeout=2.50)
            print(text)


class BaiduApi(SensitiveApi):
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.access_token = self.get_access_token()
        self.url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined?access_token=" + \
                   self.get_access_token()
        self.payload = {}
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials",
                  "client_id": "41kDxBNVEWQLtjf4X1QwQgli",
                  "client_secret": "CMKcBLn5b5j8k9NYTZGUTTxWK868h9YM"}
        return str(requests.post(url, params=params).json().get("access_token"))

    def run_apis(self):
        for text in self.data["文本内容"]:
            self.payload = f'text={text}'
            response = requests.request("POST", self.url, headers=self.headers, data=self.payload.encode('utf-8'))
            print(text)


class WordsCheckApi(SensitiveApi):
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.url = "https://api.wordscheck.com/check"
        self.payload = {"key": "VxqmjyBWoj76dQk8ZmJM6U15diKGoOOW", "content": "你好"}
        self.headers = {
            'Accept': 'application/json'
        }

    def run_apis(self):
        with open("./results/words_check_results.csv", 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["文本内容", "识别结果", "风险原因"])
            for idx, text in enumerate(self.data["文本内容"]):
                try:
                    self.payload["content"] = text
                    data = json.dumps(self.payload)
                    response = requests.request("POST", self.url, headers=self.headers, data=data)
                    response_dict = json.loads(response.text)
                    word_list = response_dict["word_list"]
                    if len(word_list) > 0:
                        check = "拒绝"
                    else:
                        check = "通过"
                    reason = ";".join([word["keyword"] + ":" + word["category"]
                                       for word in word_list])
                    print(text, check, reason)
                    csvwriter.writerows([str(idx), check, reason])
                except Exception as e:
                    csvwriter.writerows([str(idx), "ERROR", "ERROR"])
                    print(e)


class HuaweiApi:
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.url = "https://api.wordscheck.com/check"
        self.payload = {"key": "VxqmjyBWoj76dQk8ZmJM6U15diKGoOOW", "content": "你好"}
        self.headers = {
            'Accept': 'application/json'
        }

    def run_apis(self):
        with open("./results/words_check_results.csv", 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["文本内容", "识别结果", "风险原因"])
            for idx, text in enumerate(self.data["文本内容"]):
                try:
                    self.payload["content"] = text
                    data = json.dumps(self.payload)
                    response = requests.request("POST", self.url, headers=self.headers, data=data)
                    response_dict = json.loads(response.text)
                    word_list = response_dict["word_list"]
                    if len(word_list) > 0:
                        check = "拒绝"
                    else:
                        check = "通过"
                    reason = ";".join([word["keyword"] + ":" + word["category"]
                                       for word in word_list])
                    print(text, check, reason)
                    csvwriter.writerows([str(idx), check, reason])
                except Exception as e:
                    csvwriter.writerows([str(idx), "ERROR", "ERROR"])
                    print(e)
