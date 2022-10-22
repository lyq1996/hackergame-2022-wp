from textual.app import App
from rich.text import Text
from rich.panel import Panel
from textual_inputs import TextInput
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Footer, Static
import json
import asyncio
import time
import threading
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

file_handler = logging.FileHandler('logs.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Board:
    def __init__(self):
        self.b = [[i*4+j for j in range(4)] for i in range(4)]

    def _blkpos(self):
        for i in range(4):
            for j in range(4):
                if self.b[i][j] == 15:
                    return (i, j)

    def reset(self):
        for i in range(4):
            for j in range(4):
                self.b[i][j] = i*4 + j

    def move(self, moves):
        for m in moves:
            i, j = self._blkpos()
            if m == 'L':
                self.b[i][j] = self.b[i][j-1]
                self.b[i][j-1] = 15
            elif m == 'R':
                self.b[i][j] = self.b[i][j+1]
                self.b[i][j+1] = 15
            elif m == 'U':
                self.b[i][j] = self.b[i-1][j]
                self.b[i-1][j] = 15
            else:
                self.b[i][j] = self.b[i+1][j]
                self.b[i+1][j] = 15

    def __bool__(self):
        for i in range(4):
            for j in range(4):
                if self.b[i][j] != i*4 + j:
                    return True
        return False


lugstr = """                                   %                            
                              &&&&&&&&&&&&                      
                            &&&&&&&&&&&&&&&&          USTC      
               &&&&&&&&&&&&&&&&&&&  &&&&&&&&&      Hackergame   
                         &&&&&&&&&&&&&&&&&&&&         2022      
                            &&&&&&&&&&&&&&&&&&                  
                             &&&&&&&&&&&&&&&&&&&                
                            &&&&    &&&&&&&&&&&&&               
                         &&           &&&&&&&&&&&&              
                  &&&&&&&&             (&&&&&&&&&&&             
           &&&&&&&&&&&&&&                &&&&&&&&&&             
       &,,,,&&&&&&&&&&&&                 &&&&&&&&&&&&           
       ,,,,,,&&&&&&&&&&                   &&&&&&&& &&&          
       &,,&,,&&&&&&&&&                    &&&&&&& &&&&          
       &,,,,,,&&&&&&&&                    &&&&&& &&&&&&&        
        ,,,&,&,&&&&&&                     &&&&&/&&&&& &&&       
        &,,,,,,,&&&&&                     &&&&&&&&&& &&&&&      
        &,&,&,*,,&&&                      &&&& &&&&&&&          
         ,,,,,,&,&&&                     &&&& &&&&&             
         &,*,&,,,,&&                     &,  &&&&&              
         &,&,,,,*,,&               &&       &&&&&               
          ,,,,&,,&,,&         &            ,&&&&&               
          &,&,,,,,,,/   &                  && &&                
          &,&                                                   """


class Block(Widget):
    i = Reactive(15)

    def set_i(self, i):
        self.i = i

    def render(self):
        if self.i == 15:
            return Text("")
        i = self.i // 4
        j = self.i % 4
        text = '\n'.join(
            map(lambda x: x[16*j:16*j+16], lugstr.split('\n')[6*i:6*i+6]))
        return Panel(text, border_style="yellow")


class InfoWidget(Widget):
    info = Reactive({'bT': '', 'bF': '', 'ib': -1, 'inbits': [],
                    'scrambled': False, 'pc': 0, 'lb': 0, 'hl': -1})

    def set_info(self, info):
        self.info = info

    def highlight_move(self, bw):
        move = self.info[bw]
        if move:
            hl = self.info['hl']
            if hl == -1 or ['bF', 'bT'][self.info['inbits'][self.info['ib']]] != bw:
                return move
            else:
                return f"{move[:hl]}\033[32;1m{move[hl]}\033[0m{move[hl+1:]}"
        else:
            return 'No move'

    def highlight_inbits(self):
        s = ''
        for i in range(self.info['ib']):
            s += f"{self.info['inbits'][i]}"
        s += f"\033[32;1m{self.info['inbits'][self.info['ib']]}\033[0m"
        for i in range(self.info['ib']+1, len(self.info['inbits'])):
            s += f"{self.info['inbits'][i]}"
        return s

    def render(self):
        if self.info['scrambled'] and self.info['pc'] == self.info['lb'] and len(self.info['inbits']) > 0 and self.info['ib'] < 0:
            global success_flag
            success_flag = len(self.info['inbits'])
            return Panel("Success! Press q to get flag.", title="Info", border_style="green")
        if self.info['ib'] >= 0:
            return Panel(Text.from_ansi(f"Current branch ({self.info['pc']+1}/{self.info['lb']}):\n{'-'*32}\nMove 0: {self.highlight_move('bF')}\nMove 1: {self.highlight_move('bT')}\n{'-'*32}\nBecause the {self.info['ib']+1}{'st' if self.info['ib'] == 0 else ('nd' if self.info['ib'] == 1 else 'th')} bit of your inputs ({self.highlight_inbits()}) is {self.info['inbits'][self.info['ib']]},\nwe will execute Move {self.info['inbits'][self.info['ib']]}\n{'-'*32}\n"+"isScrambled? "+ ('\033[32;1m' if self.info['scrambled'] else '\033[31;1m')+str(self.info['scrambled'])+"\033[0m\n"), title="Info", border_style="green")
        else:
            return Panel(Text.from_ansi(f"All {self.info['lb']} branches have been executed.\n{'-'*32}\nisScrambled? "+"\033[31;1mFalse\033[0m\n"+f"{'-'*32}\nNot scrambled, no flag"), title="Info", border_style="green")


class BPApp(App):
    board = Board()
    pc = Reactive(0)
    blocks = [Block() for i in range(16)]
    info = InfoWidget()
    show_bar = Reactive(False)
    
    num = 0

    def __init__(self, bitlength=1, branches=[[0, '', 'U']], *args, **kwargs):
        super(BPApp, self).__init__(*args, **kwargs)
        self.bitlength = bitlength
        self.branches = branches
        self.inbits = [0]*bitlength

    def watch_pc(self, index):
        # self.num += 1
        # if self.num == 8:
        #     raise ValueError('A very specific bad thing happened.', self.inbits)
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
        

        if bool(self.board) and index == len(self.branches) and len(self.inbits) > 0 and not (index < len(self.branches)):
            logger.info("we got ans: {}".format(''.join([str(elem) for elem in self.inbits])))
            raise ValueError('Bye-bye textual')


    async def action_reset(self):
        self.pc = 0

    async def action_last(self):
        self.pc = len(self.branches)

    async def action_prev(self):
        if self.pc > 0:
            self.pc -= 1

    async def action_next(self):
        if self.pc < len(self.branches):
            self.pc += 1


    async def on_load(self, event: events.Load):
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("q", "quit", "Quit")
        await self.bind("r", "reset", "Reset")
        await self.bind("u", "prev", "Undo")
        await self.bind("e", "next", "Execute")
        await self.bind("l", "last", "ExecuteAll")
        await self.bind("t", "traverse_inbits", "TraverseInbits")

    async def on_mount(self):
        """Make a simple grid arrangement."""
        await self.view.dock(Footer(), edge="bottom")
        grid = await self.view.dock_grid(edge="left", name="board", size=80)
        grid.add_column("col", repeat=4, size=20)
        grid.add_row("row",  repeat=4, size=8)
        grid.set_align("center")
        grid.place(*self.blocks)

        await self.view.dock(self.info, size=29, edge="top", name="info")
        await self.view.dock(TextInput(name="inbits", placeholder="0"*self.bitlength, title="Inputs"), edge="right")

        for i in range(16):
            self.blocks[i].set_i(i)
        # bT   ib为true时  做什么
        # bF   ib为false时 做什么
        # inbits 输入的字符串
        # scramled 是否乱
        # pc 当前走到几
        # lb 总共多少
        self.info.set_info({'bT': self.branches[0][1],
                            'bF': self.branches[0][2],
                            'ib': self.branches[0][0],
                            'inbits': self.inbits,
                            'scrambled': bool(self.board),
                            'pc': 0,
                            'lb': len(self.branches),
                            'hl': -1})

    async def action_traverse_inbits(self):
        max_ans = pow(2, int(self.bitlength)) - 1
        for i in range(0, max_ans):
            self.inbits = list(map(int, ("{0:0"+str(self.bitlength)+"b}").format(i)))
            logger.info("self.pc: {}, self.num: {}, self.inbits: {}".format(self.pc, self.num, self.inbits))
            self.num += 1
            self.watch_pc(len(self.branches))

    async def handle_input_on_change(self, message):
        # 每当input有改动时 此函数触发
        try:
            inbits = list(map(int, message.sender.value))
            for x in inbits:
                assert x == 0 or x == 1
            assert len(inbits) == self.bitlength
            self.inbits = inbits
            # 当前0步 模拟执行0步
            # self.pc = 0设置为0 不可触发执行
            # 也就是说watch是在值发生变化时触发
            if self.pc == 0:
                self.watch_pc(0)
            else:
                self.pc = 0

        except:
            pass

success_flag = 0

def chal(bitlength, obf):
    filename = f'chals/b{bitlength}{"_obf" if obf else ""}.json'
    with open(filename) as f:
        branches = json.load(f)
    global success_flag
    success_flag = 0
    BPApp.run(bitlength=bitlength, branches=branches)
    return success_flag == bitlength

def failed():
    print("You didn't make it. No flag for you.")
    exit(0)

def success(c):
    print("success")
    # with open(f"/flag{c}") as f:
    #     print(f.read())
    exit(0)


c = int(input("\n1. 4 bits (plain)\n2. 16 bits (obfuscated)\n3. 64 bits (obfuscated)\nChoose level: "))
if c == 1:
    if not chal(4, False):
        failed()
elif c == 2:
    if not chal(16, True):
        failed()
elif c == 3:
    if not chal(64, True):
        failed()
else:
    print("Need more challenges? Maybe Hackergame 2023~")
    exit(0)

success(c)
