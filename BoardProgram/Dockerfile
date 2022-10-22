FROM python:3
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list &&\
    apt update && apt -y upgrade && \
    apt install -y socat && \
    rm -rf /var/lib/apt/lists/*

RUN pip install textual textual-inputs~=0.2.6

WORKDIR /root
RUN mkdir chals

COPY run.sh ./
COPY BP.py ./
COPY chals/* ./chals/

CMD ["socat", "exec:bash run.sh,pty,stderr,setsid,sigint,sane", "stdin!!stdout"]
