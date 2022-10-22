## 0x07 企鹅拼盘
### 这么简单我闭眼都可以！
分析题目，输入4个比特，有16步，每1步对应2个操作序列，根据4个比特中的某1个比特，决定2个选择操作序列中的哪一位。走到某一步，若拼盘复原，则失败。

所以第1问有2^4种情况，可选答案为0到16，本地模拟即可解。

### 大力当然出奇迹啦~
分析题目，输入16个比特，有256步，每1步对应2个操作序列，根据4个比特中的某1个比特，决定2个选择操作序列中的哪一位。走到某一步，若拼盘复原，则失败。

所以第2问有2^16种情况，可选答案为0到65535，本地模拟即可解。

### 1和2问的解
将程序魔改，选择难度之后，按T会遍历0到65535作为答案，若某个答案跑完了，且拼盘是弄乱的，则为正确答案，抛出异常并结束程序，悠闲的打开logs.log，即可查看flag。
```
...

    def watch_pc(self, index):
        logger.info("watch_pc run, self.inbits: {} ".format(self.inbits))

        self.board.reset()
        for branch in self.branches[:index]:
            self.board.move(branch[1] if self.inbits[branch[0]] else branch[2])
        for i in range(16):
            self.blocks[i].set_i(self.board.b[i//4][i % 4])
        
        self.info.set_info({'bT': self.branches[index][1] if index < len(self.branches) else '',
                            'bF': self.branches[index][2] if index < len(self.branches) else '',
                            'inbits': self.inbits,
                            'ib': self.branches[index][0] if index < len(self.branches) else -1,
                            'scrambled': bool(self.board),
                            'pc': index,
                            'lb': len(self.branches),
                            'hl': -1})
        
        // 注意  魔改点1！
        if bool(self.board) and index == len(self.branches) and len(self.inbits) > 0 and not (index < len(self.branches)):
            logger.info("we got ans: {}".format(''.join([str(elem) for elem in self.inbits])))
            raise ValueError('Bye-bye textual')

    async def on_load(self, event: events.Load):
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("q", "quit", "Quit")
        await self.bind("r", "reset", "Reset")
        await self.bind("u", "prev", "Undo")
        await self.bind("e", "next", "Execute")
        await self.bind("l", "last", "ExecuteAll")
        // 注意  魔改点2！
        await self.bind("t", "traverse_inbits", "TraverseInbits")

    // 注意  魔改点3！
    async def action_traverse_inbits(self):
        max_ans = pow(2, int(self.bitlength)) - 1
        for i in range(0, max_ans):
            self.inbits = list(map(int, ("{0:0"+str(self.bitlength)+"b}").format(i)))
            logger.info("self.pc: {}, self.num: {}, self.inbits: {}".format(self.pc, self.num, self.inbits))
            self.num += 1
            self.watch_pc(len(self.branches))

...

```
### 这个拼盘。。能靠掀桌子弄乱吗？
数学题，理不直气也壮的不会。
