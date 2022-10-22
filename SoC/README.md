## 0x02 片上系统
### 引导扇区
根据`PulseView`的官方文档[File format:sigrok/v2](https://sigrok.org/wiki/File_format:Sigrok/v2)，`sigrok v2`会话文件是一个标准的 `ZIP`文件，文件后缀是`.sr`。首先将题目给的附件改名为`sdcard_data_pulseview.sr`，使用`PulseView`将其打开。

`SPI`协议有4路信号。根据很久很久以前我学的知识，我推测：时钟信号基本一直存在，所以`CLK`信号是`D1`；片选信号不经常变动，所以`CS`信号是`D0`；`Master out`先于`Slave out`，所以`MOSI`信号是`D2`，`MISO`信号是`D3`。

这里的MISO信号，即为SD卡通过SPI协议发出去的信号。

于是在`PluseView`点击`Add protocol decode`，新增一个`SD card(SPI mode)`的解码器，设置信号，即可解出SD卡通过SPI协议传出去的所有data。

![](/assets/img/decode-spi.png)

右键`SPI: MISO data`，选择`Export all Annotations for this row`，将所有的`MISO`的数据导出到`MISO.txt`。


观察发现`FE`是`slave`开始传输一个`block`的标记字节，随后跟着512字节的`block`。

![](/assets/img/start-byte.png)

根据该标记将其MISO.txt分割到7个不同的bin，每个`block`512字节。
```
import re
import os

with open("./MISO.txt", "r") as f:
    lines = f.readlines()

with open("./MISO-bin", "wb") as f:
    for i in lines:
        r = re.findall("data: ([\dA-F]{2})", i)
        if r:
            f.write(bytes.fromhex(r[0]))

# 分割MISO-bin到不同的block
with open("./MISO-bin", "rb") as f:
    content = f.read()
    block_start_index = [s.start() for s in re.finditer(b"\xff\xff\xff\xfe", content)]
    
    i = 0
    for j in block_start_index:
        with open("./block"+str(i)+".bin", "wb") as f:
            f.write(content[j+4:j+4+512])
        i += 1

os.system("rm ./MISO-bin")
```

第0个bin：`block0.bin`，就是SD卡第一个扇区里面保存的`"bootloader"`了，将其`strings`一下，即可查看flag。
```
$ strings block0.bin      
flag{0K_you_goT_th3_b4sIc_1dE4_caRRy_0N}                                 
```

### 操作系统
那么1-7个block就是所谓的"操作系统了"，将其组装起来：
```
$ echo -n > ./elf
$ for i in {1..6}
do
cat block$i.bin >> ./elf
done
```

根据题目提示，这是一个RISC-V指令集的程序，所以使用qemu将其模拟润（不是）起来。
```
$ qemu-system-riscv32 -m 4G -nographic -machine virt -kernel elf -bios none  -s -S
```

然后使用交叉编译工具链提供的gdb挂上去。

```
$ riscv-none-elf-gdb
(gdb) target remote localhost:1234
Remote debugging using localhost:1234
warning: No executable has been specified and target does not support
determining executable automatically.  Try using the "file" command.
0x00001000 in ?? (
```

qnum模拟器固件加载在`0x1000`处，并且默认将`elf`加载到`0x80000000`，通过`0x1014`处的指令跳转到`0x80000000`，但是通过反汇编`bootloader`，我们可以看到，`elf`本来加载的地址应该是`0x20001000`。`bootloader`的最后一段指令如下：
```
; 读完跳转执行0x20001000，也就是"操作系统"被加载到地址0x20001000处
0x80000090:  lui     t0,0x20001  
0x80000094:  jr      t0
0x80000098:  ret
```

所以通过gdb的`restore`将`elf`恢复到内存`0x20001000`处。
```
restore /mnt/shared/SoC/elf binary 0x20001000
```

再设置把跳转地址从`0x80000000`设置到`0x20001000`：
```
set {int}0x1018=0x20001000
```

可以愉快的开始调咯，我当场边学`RISC-V`指令集边阅读反汇编代码，发现往`0x93000000`这个地址里面写了数次字符串，包括`"LED: ON"`，`"Memory OK"`，`"Video outputed"`，`"flag{"`，`"}"`，很明显这就是写入串口所使用的地址。挑出写`"LED: ON"`的汇编出来看看：
```
   0x200010bc:  addi    a3,a3,1093        ; a3 -> "ED: ON..."
   0x200010c0:  li      a2,76             ; a2 = 76 = 'L'

   0x200010c4:  lw      a5,0(a4)          ; 从 0x93000008 读取到a5                     ; 估计是串口ok的标识？
   0x200010c8:  beqz    a5,0x200010c4     ; if a5 == 0 goto 0x200010c4                ; 一直到a5等于0才继续往下走
   0x200010cc:  sw      a2,0(a6)          ; 将a2写入到0x93000000地址里  初始值是'L' 然后是 "ED: ON"   ; 很明显这是串口输出

   0x200010d0:  lw      a5,0(a4)          ; 从 0x93000008 读到a5
   0x200010d4:  beqz    a5,0x200010d0     ; 估计是串口ok的标识？
   
   0x200010d8:  addi    a3,a3,1           ; a3 = a3 + 1  初始值 指向 "D: ON.."
   0x200010dc:  lbu     a2,-1(a3)         ; a2 = a2 - 1  初始值 指向 "ED: ON.."
   0x200010e0:  bnez    a2,0x200010c4     ; 循环打印字符
```

一翻阅读，发现我们只需要关注下面的指令即可，因为这段指令夹在串口输出`"flag{"`和`"}"`中间，这里当然就是通过串口输出flag中间部分的指令。
```
   0x20001328:  lui     a0,0x20001
   0x2000132c:  addi    a0,a0,24          ; a0 = a0 + 24 = 0x20001018
   0x20001330:  jal     ra,0x20001018     ; 输出flag中间的部分 20001018

   0x20001334:  lui     a0,0x20001
   0x20001338:  lui     a5,0xdeadc
   0x2000133c:  addi    a5,a5,-273
   0x20001340:  addi    a0,a0,108
   0x20001344:  xor     a0,a0,a5
   0x20001348:  jal     ra,0x20001018     ; 输出flag中间的部分 feadae83
   0x2000134c:  li      a0,224
   0x20001350:  jal     ra,0x20001018     ; 输出flag中间的部分 000000e0
   0x20001354:  lw      a3,1176(s1)
   0x20001358:  lw      a2,1180(s0)
```

上面的指令跳转了`0x20001018`三次，分三个部分将flag的中间部分通过串口输出，我不想再思考`0x20001018`处的指令的具体逻辑了，反正只要知道`0x20001018`会走到`0x20001054`：
```
   0x20001054:  sw      a3,0(a7)
```
而`0x20001054`这里和上面输出`"LED: ON"`到串口的`0x200010cc`如出一辙，`a7`是串口的地址`0x93000000`，`a3`是要写的字符。所以把断点断在`0x20001054`，将`a3`寄存器循环打印出来，即可获取flag中间部分。

当然，手动`break`然后`p`，也太憨了。这里使用gdb脚本，一键打出flag。

如下所示，这里在运行时对内存做了一点小小的patch，不然跑飞。
```
# (gdb) source load_elf.gdb 
# (gdb) load_elf
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
```

运行方法：

终端1:
```
$ qemu-system-riscv32 -m 4G -nographic -machine virt -kernel elf -bios none  -s -S
```

终端2:
```
$ riscv-none-elf-gdb
GNU gdb (xPack GNU RISC-V Embedded GCC x86_64) 12.1
...
(gdb) source load_elf.gdb 
(gdb) load_elf
warning: No executable has been specified and target does not support
determining executable automatically.  Try using the "file" command.
0x00001000 in ?? ()
Restoring binary file /mnt/shared/SoC/elf into memory (0x20001000 to 0x20001c00)
Breakpoint 1 at 0x200010f0

Breakpoint 1, 0x200010f0 in ?? ()
Breakpoint 2 at 0x20001054

Breakpoint 2, 0x20001054 in ?? ()
$1 = 50 '2'

Breakpoint 2, 0x20001054 in ?? ()
$2 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$3 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$4 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$5 = 49 '1'

Breakpoint 2, 0x20001054 in ?? ()
$6 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$7 = 49 '1'

Breakpoint 2, 0x20001054 in ?? ()
$8 = 56 '8'

Breakpoint 2, 0x20001054 in ?? ()
$9 = 102 'f'

Breakpoint 2, 0x20001054 in ?? ()
$10 = 101 'e'

Breakpoint 2, 0x20001054 in ?? ()
$11 = 97 'a'

Breakpoint 2, 0x20001054 in ?? ()
$12 = 100 'd'

Breakpoint 2, 0x20001054 in ?? ()
$13 = 97 'a'

Breakpoint 2, 0x20001054 in ?? ()
$14 = 101 'e'

Breakpoint 2, 0x20001054 in ?? ()
$15 = 56 '8'

Breakpoint 2, 0x20001054 in ?? ()
$16 = 51 '3'

Breakpoint 2, 0x20001054 in ?? ()
$17 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$18 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$19 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$20 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$21 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$22 = 48 '0'

Breakpoint 2, 0x20001054 in ?? ()
$23 = 101 'e'

Breakpoint 2, 0x20001054 in ?? ()
$24 = 48 '0'
(gdb) 
```

flag为`flag{20001018feadae83000000e0}`。
