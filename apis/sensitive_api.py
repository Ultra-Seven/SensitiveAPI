import csv
import json
import hashlib
import pandas as pd
import requests
import time
import random
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkmoderation.v3.region.moderation_region import ModerationRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkmoderation.v3 import *
from gmssl import sm3, func
import urllib.request as urlrequest
import urllib.parse as urlparse


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

class YidunApi:
    __author__ = 'yidun-dev'
    __date__ = '2019/11/27'
    __version__ = '0.2-dev'
    API_URL = "http://as.dun.163.com/v5/text/check"
    VERSION = "v5.2"


    def __init__(self, path, secret_id, secret_key, business_id, topk=5000):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.business_id = business_id
        self.data = pd.read_csv(path)[:topk]

    def gen_signature(self, params=None):
        """生成签名信息
        Args:
            params (object) 请求参数
        Returns:
            参数签名md5值
        """
        buff = ""
        for k in sorted(params.keys()):
            buff += str(k) + str(params[k])
        buff += self.secret_key
        if "signatureMethod" in params.keys() and params["signatureMethod"] == "SM3":
            return sm3.sm3_hash(func.bytes_to_list(bytes(buff, encoding='utf8')))
        else:
            return hashlib.md5(buff.encode("utf8")).hexdigest()

    def check(self, params):
        """请求易盾接口
        Args:
            params (object) 请求参数
        Returns:
            请求结果，json格式
        """
        params["secretId"] = self.secret_id
        params["businessId"] = self.business_id
        params["version"] = self.VERSION
        params["timestamp"] = int(time.time() * 1000)
        params["nonce"] = int(random.random() * 100000000)
        # params["signatureMethod"] = "SM3"  # 签名方法，默认MD5，支持SM3
        params["signature"] = self.gen_signature(params)

        try:
            params = urlparse.urlencode(params).encode("utf8")
            request = urlrequest.Request(self.API_URL, params)
            content = urlrequest.urlopen(request, timeout=10).read()
            return json.loads(content)
        except Exception as ex:
            print("调用API接口失败:", str(ex))

    def run_apis(self):
        texts: list = []
        with open("./results/yidun_results.csv", 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["文本内容", "识别结果", "风险原因"])
            for idx, text in enumerate(self.data["文本内容"]):
                text_param = {
                    "dataId": f"{idx}",
                    "content": text
                }
                texts.append(text_param)
            nr_groups = len(texts) // 100 + 1
            for g_idx in range(nr_groups):
                start_idx = g_idx * 100
                end_idx = (g_idx + 1) * 100
                batch = texts[start_idx:end_idx]
                for offset, param in enumerate(batch):
                    idx = start_idx + offset
                    ret = self.check(param)
                    code: int = ret["code"]
                    msg: str = ret["msg"]
                    if code == 200:
                        result: dict = ret["result"]
                        antispam: dict = result["antispam"]
                        taskId: str = antispam["taskId"]
                        suggestion: int = antispam["suggestion"]
                        labelArray: list = antispam["labels"]
                        if suggestion == 0:
                            csvfile.write(f"{idx},通过,NA\n")
                            print("taskId: %s, 文本机器检测结果: 通过" % taskId)
                        elif suggestion == 1:
                            label = ";".join([str(l["label"]) for l in labelArray])
                            csvfile.write(f"{idx},嫌疑,{label}\n")
                            print("taskId: %s, 文本机器检测结果: 嫌疑, 需人工复审, 分类信息如下: %s" % (
                            taskId, labelArray))
                        elif suggestion == 2:
                            label = ";".join([str(l["label"]) for l in labelArray])
                            csvfile.write(f"{idx},拒绝,{label}\n")
                            print("taskId=%s, 文本机器检测结果: 不通过, 分类信息如下: %s" % (taskId, labelArray))
                    else:
                        print("ERROR: code=%s, msg=%s" % (ret["code"], ret["msg"]))
                    # time.sleep(1)