#!/bin/bash
gcc pwn.c -o pwn
gcc chall.c -o chall
tar -zcf pwn.tar.gz pwn
cat pwn.tar.gz | base64 -w0 > pwn_encode