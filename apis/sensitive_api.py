import csv
import json

import pandas as pd
import requests
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkmoderation.v3.region.moderation_region import ModerationRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkmoderation.v3 import *


class SensitiveApi:
    def __int__(self, path):
        print("")


class BaiduApi(SensitiveApi):
    def __init__(self, path, topk=5000):
        self.data = pd.read_csv(path)[:topk]
        self.access_token = self.get_access_token()
        self.url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined?access_token=" + \
                   self.get_access_token()
        self.payload = {}
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        self.name = "baidu"

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
        with open("./results/baidu_results.csv", 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["文本内容", "识别结果", "风险原因"])
            for idx, text in enumerate(self.data["文本内容"]):
                self.payload = f'text={text}'
                response = requests.request("POST", self.url, headers=self.headers, data=self.payload.encode('utf-8'))
                print(response.text)
                response_dict = json.loads(response.text)
                conclusion = response_dict["conclusion"]
                if conclusion == "合规":
                    csvfile.write(f"{idx},通过,NA\n")
                    print(f"{idx},通过,NA\n")
                else:
                    data = response_dict["data"]
                    reason_list = []
                    for r in data:
                        reason = r["msg"]
                        reason_list.append(reason)
                    reason_text = ";".join(reason_list)
                    csvfile.write(f"{idx},拒绝,{reason_text}\n")
                    print(f"{idx},拒绝,{reason_text}\n")


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
    def __init__(self, path, topk=5000):
        self.data = pd.read_csv(path)[:topk]
        # project_id = "3113a77e663b481bbe85e035a576e52e"
        ak = "2KNPQIFEQLXVNJ6HUQ3J"
        sk = "h9Gi6OvDlF5AJMa5ay0eR4oVtbZlVwyqF8zmxuOw"

        credentials = BasicCredentials(ak, sk)
        self.client = ModerationClient.new_builder().with_credentials(credentials)\
            .with_region(ModerationRegion.value_of("cn-north-4"))\
            .build()

    def run_apis(self):
        with open("./results/huawei_results.csv", 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["文本内容", "识别结果", "风险原因"])
            for idx, text in enumerate(self.data["文本内容"]):
                try:
                    request = RunTextModerationRequest()
                    databody = TextDetectionDataReq(
                        text=text
                    )
                    request.body = TextDetectionReq(
                        data=databody,
                        event_type="comment"
                    )
                    response = self.client.run_text_moderation(request)
                    response_dict = response.result
                    conclusion = response_dict.suggestion
                    if conclusion == "pass":
                        csvfile.write(f"{idx},通过,NA\n")
                        print(f"{idx},通过,NA")
                    else:
                        data = response_dict.details
                        reason_list = []
                        for r in data:
                            reason = r.label
                            words = "-".join([t.segment for t in r.segments])
                            reason_list.append(f"{reason}:{words}")
                        reason_text = ";".join(reason_list)
                        csvfile.write(f"{idx},拒绝,{reason_text}\n")
                        print(f"{idx},拒绝,{reason_text}")
                    print(response_dict)
                except exceptions.ClientRequestException as e:
                    csvfile.write(f"{idx},NA,NA\n")
                    print(f"{idx},NA,NA\n")
