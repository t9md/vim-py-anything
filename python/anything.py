# -*- coding: utf8 -*-
import vim
import sys
import re
import os

__all__ = (
    'vim', 
    'AnythingSource',
    'anything'
)

# alias
vim.cmd = vim.command
vim.normal = lambda cmd: vim.command("normal! " + cmd.replace('<','\<'))
vim.normal_map = lambda cmd: vim.command("normal " + cmd.replace('<','\<'))
vim.insert = lambda n,l: vim.current.buffer.range(n,n).append(l)
vim.current_buffer_dir = lambda: os.path.dirname(vim.current.buffer.name)

def __vim_prompt(ask = 'input', mode = 'cui'):
  if mode == 'cui':
    answer = vim.eval("input('%s')" % ask)
  else:
    answer = vim.eval("inputdialog('%s')" % ask)
  return answer

vim.prompt = __vim_prompt
#------------------------------------------------------------------
# AnythingSource
#########################
class AnythingSource(object):
    """docstring for Commmand"""
    volatile = False
    def __init__(self,name):
        super(AnythingSource, self).__init__()
        self.name = name

    def view(self):
        """docstring for view"""
        if hasattr(self, 'view_trans'):
            f = self.view_trans
        else:
            f = lambda x: x
        return [ f(s) for s in self.candidate ]

    def action(self):
        """docstring for action"""
        pass

# Anything Controller
#########################
class Anything(object):
    """docstring for Anything"""

    #########################
    # Window
    #########################
    class Window(object):
        """docstring for Window"""
        win_height_max = 80
        windows = []
        curbuf = vim.current.buffer
        def __init__(self):
            super(Anything.Window,self).__init__()
            self.init()

        def init(self):
            self.save()
            split_location = 'botright'
            cmd = "silent! %s 1split /tmp/anything-buffer" % split_location
            vim.command(cmd)
            vim.command("syn match AnythingCommandDesc '   .*$'")
            vim.command("syn match AnythingSelection   '> .*$'")
            vim.command("syn match AnythingNotFound    '  NO MATCH'")
            vim.command('hi def link AnythingCommandDesc Function')
            vim.command('hi def link AnythingNotFound    Error')
            vim.command('hi          AnythingSelection   guibg=#293739')
            vim.command('setlocal nocursorline')

        def update(self, lis):
            del vim.current.buffer[:]
            if len(lis) == 0:
                lis = ['  NO MATCH']
            else:
                lis = [ "  %-21s   %-10s" % (name, doc) for name, doc in lis ]
                lis[0] = '>' + lis[0][1:]

            vim.current.buffer.range(0,0).append(lis)
            vim.current.window.height = min(len(lis), self.win_height_max)
            
        def finish(self):
            self.src_page_idx = 0
            self.restore()

        def save(self):
            self.windows = [ (idx, win.height) for idx, win in enumerate(vim.windows) ]

        def restore(self):
            for idx, height in sorted(self.windows, reverse=True, key=lambda win: win[1]):
                if idx < len(vim.windows): vim.windows[idx].height = height

    # Echoline
    #########################
    class Echoline(object):
        """docstring for Echoline"""
        # prompt = " >> "
        def __init__(self, prompt=None):
            if prompt: self.prompt = prompt
            self.init()

        def init(self):
            pass

        def __draw(self,lis):
            vim.command('redraw')
            for highight, text in lis:
                vim.command("echohl " + highight)
                vim.command("echon '%s'" % text)
            vim.command('echohl None')

        def update(self, prompt, msg):
            self.__draw([ ('Comment', prompt), ('Number', msg), ('Function', '|') ])
        def print_result(self,msg):
            self.__draw([('Comment', "[result] "), ('Directory', msg)])

    #########################
    # Keybind
    #########################
    class Keybind(object):
        """docstring for Keybind"""
        def __init__(self, name):
            super(Anything.Keybind,self).__init__()
            self.name = name
            self.init()

        def init(self):
            lower_alpha = "abcdefghijklmnopqrstuvwxyz"
            upper_alpha = lower_alpha.upper()
            numbers     = "0123456789"
            # punctuation = '<>`@#~!"$%&/()=+*-_.,;:?\\\'{}[] ' # and space
            punctuation = '<>`@#~!"$%&/()=+*-_.,?\\\'{}[] ' # and space
            chars = lower_alpha + upper_alpha + numbers + punctuation
            # chars = lower_alpha + numbers
            # chars = numbers
            vim.command("setlocal timeout")
            vim.command("setlocal timeoutlen=0")
            vim.command("setlocal nonumber")
            fmt = "nnoremap <silent> <buffer> <Char-%s> :python " + self.name + ".normal_key(%s)<CR>"
            lis = [ fmt % (ord(char), ord(char)) for char in chars ]
            for cmd in lis: vim.command(cmd)

            fmt = "nnoremap <silent> <buffer> %s :python " + self.name + ".special_key('%s')<CR>"
            special_keys = { 
                    'CursorHead'           : '<C-a>',
                    'CursorEnd'            : '<C-e>',
                    'Backspace'            : ['<C-h>','<BS>'],
                    'AcceptSelection'      : '<CR>',
                    'Cancel'               : ['<C-g>','<C-c>', '<Esc>','<D-j>'],
                    'NextLine'             : '<C-n>',
                    'PreviousLine'         : '<C-p>',
                    # 'SelectAction'       : '<Tab>',
                    'ClearLine'            : ['<C-u>','<D-u>'],
                    'DeleteBackwordWord'   : '<C-w>',
                    'WinsizeIncrease'      : '<C-o>',
                    'WinsizeDecrease'      : '<C-[>',
                    # 'ShowHelp'           : '<f1>',
                    'SwitchSourceNext'     : '<Tab>',
                    'SwitchSourcePrevious' : '<S-Tab>',
                    'SwitchSource_1'       : '<f1>',
                    'SwitchSource_2'       : '<f2>',
                    'SwitchSource_3'       : '<f3>',
                    }

            vim_cmd_list = []
            for func, key in special_keys.items():
                if type(key) == list:
                    vim_cmd_list.extend( [ fmt % (k, func) for k in key] )
                else:
                    vim_cmd_list.append( fmt % (key, func) )
            for cmd in vim_cmd_list: vim.command(cmd)


    #########################
    # Main Controller
    #########################
    current_input = ""
    def __init__(self, name):
            # , source, source_b=None):
        super(Anything,self).__init__()
        self.name = name
        self.src_page_idx = 0

    def start(self, src, ac_src_dict=None, mode='n'):
        self.ac_src_dict = ac_src_dict
        self.mode = mode
        self.source = src

        self.init()

        self.window   = self.Window()
        self.echoline = self.Echoline()
        self.keybind  = self.Keybind(self.name)

        self.init_interactive()

    def init(self):
        self.range  = vim.current.range
        self.initial_window = vim.current.window
        self.initial_buffer = vim.current.buffer

    def init_interactive(self):
        if self.source.volatile:
            self.source.candidate = self.source.prepare_candidate()
        if hasattr(self.source, "candidate_" + self.mode ):
            self.source.candidate = getattr(self.source, "candidate_" + self.mode)

        self.window.update(self.source.view())
        self.refresh_screen()

    def run(self, command):
        self.init()
        command()

    def finish(self):
        self.do_ClearLine()
        vim.command("bdelete!")
        vim.command("wincmd p")
        self.window.finish()
        vim.command("set timeoutlen=1000")

    def test(self):
        print self.initial_range

    def update_candidate(self):
        candidate = self.source.view()
        candidate = self.build_candidate(candidate, self.current_input)
        self.window.update(candidate)

    def build_candidate(self, source, ptns):
        if not len(ptns):
            return source

        candidate = [ cmd for cmd, doc in source ]
        search = ".*%s.*" % '.*'.join(ptns.split())
        result = [ cmd_name for cmd_name in candidate if re.match(search, cmd_name, re.I)]

        if not len(result) and len(ptns.split()) == 1:
            abbr_list = []
            for cmd in candidate:
                li = self.source.split_pattern.split(cmd)
                try:
                    abbr_list.append((li[0][:2] + '.*' +  ".*".join(a[0] for a in li [1:]), cmd))
                    # abbr_list.append((li[0][:2] + '.*' + li[1:2][0][0] + ".*", cmd))
                    # abbr_list.append((li[0][:2] + '.*' + li[1:2][0][0] + ".*", cmd))
                except IndexError:
                    pass
            # return abbr_list
            result = [ cmd for abbr, cmd in abbr_list if re.match(abbr, ptns.split()[0], re.I) ]
        return [ (cmd, doc) for cmd, doc in source if cmd in result ]

    def normal_key(self,key):
        self.current_input += chr(key)
        self.update_candidate()
        self.refresh_screen()

    # special key event handling
    def special_key(self, command):
        meth_name = 'do_' + command
        if hasattr(self, meth_name):
            method = getattr(self, meth_name)
        elif hasattr(self.echoline, meth_name):
            method = getattr(self.echoline, meth_name)
        else:
            raise
        method()

    def do_Cancel(self):
        self.finish()

    def do_AcceptSelection(self):
        selected_word = vim.current.line[2:].split()[0]
        org_line = vim.current.line
        if selected_word == 'NO': return

        self.do_ClearLine()
        let = 0
        # func = eval(selected_word)
        try:
            vim.command("bdelete!")
            vim.command("wincmd p")
            vim.command("redraw!")
            vim.command("set timeoutlen=1000")
            let = self.source.action(selected_word, org_line)
        # except Exception, e:
            # self.echoline.print_result(e)
        finally:
            self.src_page_idx = 0
            self.echoline.print_result(let)

    def refresh_screen(self):
        self.echoline.update(self.source.name + " >> ", self.current_input)

    def redraw(self):
        self.update_candidate()
        self.refresh_screen()

    def do_ClearLine(self):
        self.current_input = ""
        self.redraw()

    def do_CursorHead(self): pass
    def do_CursorEnd(self): pass

    def do_ShowHelp(self): pass

    def do_SwitchSource(self, src_num):
        self.source = self.ac_src_dict[src_num]
        self.current_input = ""
        self.init()
        self.init_interactive()

    def do_SwitchSource_1(self): self.do_SwitchSource(1)
    def do_SwitchSource_2(self): self.do_SwitchSource(2)
    def do_SwitchSource_3(self): self.do_SwitchSource(3)
    def do_SwitchSourceNext(self):
        self.src_page_idx = (self.src_page_idx + 1 ) % len(self.ac_src_dict) 
        self.do_SwitchSource(self.src_page_idx)

    def do_SwitchSourcePrevious(self):
        page = (self.src_page_idx - 1 )
        if page < 0: page = len(self.ac_src_dict) - 1
        self.src_page_idx = page
        self.do_SwitchSource(page)

    def do_DeleteBackwordWord(self):
        s = ' '.join(self.current_input.split()[:-1])
        if len(s) != 0: s += ' '
        self.current_input = s
        self.redraw()

    def do_Backspace(self):
        self.current_input = self.current_input[:-1]
        self.redraw()

    def __line_move(self, direction):
        vim.current.line = ' ' + vim.current.line[1:]
        vim.normal(direction)
        vim.current.line = '>' + vim.current.line[1:]

    def do_NextLine(self):     self.__line_move('j')
    def do_PreviousLine(self): self.__line_move('k')

anything = Anything("anything")
