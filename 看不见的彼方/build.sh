#!/bin/bash
gcc A.c -o A
gcc B.c -o B
cat A | base64 - > /exe
echo -n "@" >> /exe
cat B | base64 - >> /exe
cp A /home/pwn/A/exe
cp B /home/pwn/B/exe 