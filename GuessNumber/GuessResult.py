from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import re

host = ('0.0.0.0', 8000)

def guess():
    url = "http://202.38.93.111:18000/state"
    token = "Bearer 1741:MEQCICzlD+fNmcAGS0O7IFWin2Nt2McUtku/NB21icx61Uq/AiAtFd6hCxgUvdeSE/R8888eFoJ4TytvoVVbkDjvbZEogw=="
    auth = {"authorization": token}

    guess_range = [0, 500000, 1000000]

    # 先用0.500000直接猜测 获得是大还是小的hit
    requests.post(
        url, headers=auth, data="<state><guess>0.500000</guess></state>")

    while True:
        guess_result = requests.get(url, headers=auth)

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
                print("[*] we got")
                return str(next_guess).encode()

            a = requests.post(url, headers=auth, data="<state><guess>"+str(next_guess)+"</guess></state>", timeout=0.1)
                    
        else:
            print("[*] guess with no luck")
            break

class Request(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(guess())


server = HTTPServer(host, Request)
print("start payload server at %s:%s" % host)
server.serve_forever()