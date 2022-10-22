from urllib import parse

import requests
import re
import time


session = ".eJwVkMtOAmEMhd9ltpLQ-9-SsEAuBhMwXsDEJTAiokxMRkSN727pqjlNz3fa36qtT23Vq9DMREHZXMDCgLxDVgidQIFY0dGZILyw5UCZTFmNAjsEHqZFkFksVHIqlCKRgZFiOqSfdQoUYAkNZgMAVEQuyIipqrqaJjmxDuIlPMWEeLiGeeYJK0VAHRUiSmIlECkkxFADihVQQUJOjCfBijGn3TmQFyEGE3EnDM4VztBpo5Z9uGjVqdpmXx_Ov8hTerPx7XA6_HkbXTzP39eDq3u4KdPJ4-5A85Zm60W7_-zOLwl365Ph4qM72A3aycZehqft4rip78fdO8-qJ821PHy3x2a5XO1Hr8fV07jZfvX71d8_vQ1bqA.Y1QEaA.k6urRxVD94OcqrYikZfOc2crNHg"

res = requests.get("http://202.38.93.111:10047/xcaptcha", cookies={"session": session})

content = res.content
new_session = res.cookies.get_dict()['session']

result = re.findall(r"(\d+)\+(\d+)", content.decode())
if result:
    captcha = [""] * 3
    index = 0
    for i in result:
        captcha[index] = str(int(i[0]) + int(i[1]))
        index += 1

    captcha1 = captcha[0]
    captcha2 = captcha[1]
    captcha3 = captcha[2]

payload = parse.urlencode({"captcha1": captcha1, "captcha2": captcha2, "captcha3": captcha3})

headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'Content-Length': str(len(payload)), 
           "Referer": "http://202.38.93.111:10047/xcaptcha",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}


res = requests.post("http://202.38.93.111:10047/xcaptcha",
                    data=payload, cookies={"session": new_session}, headers=headers, proxies={"http": "127.0.0.1:8080"})
print((res.content).decode())
