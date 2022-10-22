from time import sleep
import requests
import re
import time
import sys

def main():
    url = "http://202.38.93.111:18000/state"
    token = "Bearer 1741:MEQCICzlD+fNmcAGS0O7IFWin2Nt2McUtku/NB21icx61Uq/AiAtFd6hCxgUvdeSE/R8888eFoJ4TytvoVVbkDjvbZEogw=="
    auth = {"authorization": token}

    i = 0

    while True:
        guess_range = [0, 500000, 1000000]
        game_over = 0

        # 先用0.500000直接猜测 获得是大还是小的hit
        requests.post(
            url, headers=auth, data="<state><guess>0.500000</guess></state>")

        while True:
            while True:
                try:
                    guess_result = requests.get(url, headers=auth, timeout=0.1)
                    if guess_result.content:
                        break
                except requests.exceptions.Timeout:
                        # print("[*] timeout but continue")
                        continue

            content = guess_result.content.decode()
            match_res = re.findall("\">(.*)<\/guess>", content)
            if match_res:
                guess = int(float((match_res)[0]) * 1000000)
                # save current guess
                guess_range[1] = guess
                if "less=\"true\"" in content:
                    guess_range[0] = guess
                elif "more=\"true\"" in content:
                    guess_range[2] = guess
                # next guess
                next_guess = round(
                    float((guess_range[0] + guess_range[2])/2.0) * 0.000001, 6)
                print("[*] next_guess: ", next_guess)
                if guess_range[0] + 2 == guess_range[2]:
                    print("[*] go to exit")
                    sys.exit()
                
                while True:
                    try:
                        a = requests.post(
                            url, headers=auth, data="<state><guess>"+str(next_guess)+"</guess></state>", timeout=0.1)
                        if a.status_code == 204:
                            break
                    except requests.exceptions.Timeout:
                        # print("[*] timeout but continue")
                        continue
            else:
                if "<talented>1</talented>" in content:
                    print("[*] game over: \n" + content)
                    game_over = 1
                print("[*] guess round: ", i, "with game over: ", game_over)
                i += 1
                break
        if game_over:
            break
        break

if __name__ == "__main__":
    main()
