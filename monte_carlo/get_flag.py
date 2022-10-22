# coding: utf-8

from calendar import c
from pwn import *
import time
import sys
import subprocess
import tempfile

# context.log_level = 'debug'
# 本地验证
remote_enable = False

token = "1741:MEQCICzlD+fNmcAGS0O7IFWin2Nt2McUtku/NB21icx61Uq/AiAtFd6hCxgUvdeSE/R8888eFoJ4TytvoVVbkDjvbZEogw=="

# 暴力破解100次clock节拍
clocks = {}
for i in range(100):
    if remote_enable:
        p = remote("202.38.93.111", 10091)
        p.recvuntil(b"token: ")
        p.sendline(token.encode())
    else:
        p = process("./test")

    ans = []
    for _ in range(3):
        p.recvuntil("：".encode())
        p.sendline(b"3.14159")
        p.recvuntil("是：".encode())
        ans.append(p.recvline().rstrip(b'\n').decode())
    p.close()

    timestamp = int(time.time())
    print("[+] Result: {}, timestamp: {}".format(ans, timestamp))

    sub_ps = []
    # 开16个进程 爆破clock 
    # 为什么不在monte_carlo里面用多线程？因为srand是线程共享的 某个线程设置 会影响别的线程
    # 猜测clock的范围是 0 - 2400
    for j in range(0, 16):
        f = tempfile.NamedTemporaryFile()
        sub_p = subprocess.Popen(["./monte_carlo", "0", str(timestamp), ans[0], ans[1], ans[2], str(j * 150), str((j+1)*150)],
                                 stdout=f, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        sub_ps.append((sub_p, f))

    clock = -1
    for p, f in sub_ps:
        p.wait()
        f.seek(0)
        sub_stdout = f.read().decode().rstrip("\n")
        if sub_stdout != "-1":
            # 获得了clock
            clock = sub_stdout
        f.close()

    # 保存到文本里 以供后续分析
    clock_collect = open("./clock_collect", "a")
    clock_collect.write(clock+"\n")
    clock_collect.close()
    print("[+] Get clock: {}".format(clock))
    if clock not in clocks:
        clocks[clock] = 1
    else:
        clocks[clock] += 1
    time.sleep(8)

# clock 大概在750左右
# clock = str(748)
clock = max(clocks, key=clocks.get)
count = 0
print("[*] use clock: ", clock)
while True:
    timestamp = int(time.time())
    sub_p = subprocess.run(["./monte_carlo", "1", str(timestamp), clock],
                           stdout=subprocess.PIPE)

    if remote_enable:
        p = remote("202.38.93.111", 10091)
        p.recvuntil(b"token: ")
        p.sendline(token.encode())
    else:
        p = process("./test")

    result = sub_p.stdout.decode().split("\n")[0:-1]

    j = 0
    r = ""
    for i in range(0, 3):
        a = p.recvuntil("）：".encode())
        p.sendline(result[i].encode())

        r = p.recvline().decode().strip("\n")
        print("[*] i: {}, r: {}".format(i, r))
        if "猜对了！" in r:
            j += 1
        else:
            print("[*] right ans: {}, your ans: {}".format(
                p.recvline().rstrip(b"\n").decode().split("：")[-1], result[i]))
            break


    if (j == 3):
        print("[+] successed: {}".format(p.recvall().decode()))
        print("[+] guess count: {}".format(count))
        sys.exit()
    count += 1
    p.close()
    time.sleep(8)
