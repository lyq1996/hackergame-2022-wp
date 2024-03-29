#!/bin/bash
set -xe
head -n 3 /root/app2/base.tex > /dev/shm/result.tex
cat /dev/shm/input.tex >> /dev/shm/result.tex
tail -n 2 /root/app2/base.tex >> /dev/shm/result.tex
cd /dev/shm
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape result.tex
pdfcrop result.pdf
mv result-crop.pdf /root/app2/result.pdf
pdftoppm -r 300 result.pdf > result.ppm
pnmtopng result.ppm > $1
OMP_NUM_THREADS=1 convert $1 -trim $1
