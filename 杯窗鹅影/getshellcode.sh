#!/bin/bash
nasm -f elf32 -o shellcode.o shellcode.asm
ld -melf_i386 -o shellcode shellcode.o
objdump -d shellcode | grep '[0-9a-f]:' | grep -v 'file' | cut -f2 -d: | cut -f1-6 -d ' '| tr -s ' '| tr '\t' ' '| sed 's/ $//g' | sed 's/ /\\x/g' | paste -d '' -s | sed 's/^/"/' | sed 's/$/"/g'