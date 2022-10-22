import re
import os

with open("./MISO.txt", "r") as f:
    lines = f.readlines()

with open("./MISO-bin", "wb") as f:
    for i in lines:
        r = re.findall("data: ([\dA-F]{2})", i)
        if r:
            f.write(bytes.fromhex(r[0]))

# 分割MISO-bin到不同的block
with open("./MISO-bin", "rb") as f:
    content = f.read()
    block_start_index = [s.start() for s in re.finditer(b"\xff\xff\xff\xfe", content)]
    
    i = 0
    for j in block_start_index:
        with open("./block"+str(i)+".bin", "wb") as f:
            f.write(content[j+4:j+4+512])
        i += 1

os.system("rm ./MISO-bin")