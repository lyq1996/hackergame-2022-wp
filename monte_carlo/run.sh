#!/bin/bash
./build.sh

# get_flay中的remote_enable
# 为false则本地验证
# 为true则链接平台
python3 get_flag.py
