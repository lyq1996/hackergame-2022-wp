define load_elf
    set confirm off
    target remote localhost:1234
    # 加载二进制到指定内存
    restore /mnt/shared/SoC/elf binary 0x20001000
    # 设置跳转地址
    # 从0x1014跳转到0x20001000 而不是默认的0x80000000执行
    set {int}0x1018=0x20001000
    # bypass 对0x93000008的检查
    set {int}0x93000008=1
    # 断在内存初始化前面
    b *0x200010f0
    c
    # 不进行内存初始化 因为我测试中跑飞了
    set $pc=0x20001164
    # 输出"flag{"之后 会jmp 0x20001018
    # 把断点断在串口写入那里 也就是0x20001054
    # 然后打印要往串口写的字符即可
    b *0x20001054
    set $i = 0
    # 循环print 存放在a3寄存器里的字符（即要打印的字符）
    while($i<24)
        c
        p/c $a3
        set $i = $i + 1
    end
    # 20001018feadae83000000e0
end