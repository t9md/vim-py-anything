# -*- coding: utf8 -*-
import vim
import sys
import re
import os
import appscript
from anything import *

cmd_list = []
decorator_with_args = lambda f: lambda *args, **kwargs: lambda func: f(func, *args, **kwargs)

@decorator_with_args
def vimpy_cmd(f, mode='n'):
    lis.append(f)
    f.actionlist = []
    f.mode = mode
    return f

@decorator_with_args
def vimpy_command(f, mode='n'):
    """Hook to register function as vimpy_command

    This function must come firt in the file
    """
    cmd_list.append(f)
    f.actionlist = []
    f.mode = mode
    return f

@vimpy_command(mode='v')
def surround_text(header=None, footer=None):
    """Surround selected text with header and footer """
    # header, footer):
    if not header: header = vim.prompt("header? :")
    if not footer: footer = vim.prompt("footer? :")
    cr = ac_cmd.initial_range
    new_text = [header] + cr[:] + [footer]
    cr[:] = None
    vim.insert(cr.start,new_text)

@vimpy_command(mode='v')
def align_evalcomment():
    """Align with '# =>'"""
    cr = ac_cmd.initial_range
    cmd = "%d,%dAlign \"%s\"" % (cr.start, cr.end, "# =>")
    vim.command(cmd)

def transform_selection(f):
    cr = ac_cmd.initial_range
    new_text = [ f(line) for line in cr[:]]
    cr[:] = None
    vim.insert(cr.start, new_text)
    vim.normal("V%dj" % (len(new_text) - 1) )

@vimpy_command(mode='v')
def html_escape_selection():
    """HTML escape for selection"""
    transform_selection(html_escape)

@vimpy_command(mode='v')
def eval_python():
    """HTML escape for selection"""
    cr = ac_cmd.initial_range
    eval(cr[:])

@vimpy_command(mode='v')
def insert_eval_python():
    """HTML escape for selection"""
    cr = ac_cmd.initial_range
    let = [ repr(eval(exp)) for exp in cr[:] ]
    vim.insert(cr.end+1, let)

@vimpy_command(mode='v')
def html_unescape_selection():
    """HTML unescape for selection"""
    transform_selection(html_unescape)

@vimpy_command(mode='v')
def upper_selection():
    """選択範囲を大文字にする。"""
    transform_selection(lambda x: x.upper() )

@vimpy_command(mode='v')
def lower_selection():
    """選択範囲を小文字にする。"""
    transform_selection(lambda x: x.lower() )

@vimpy_command()
def todo():
    """Open Todo List"""
    vim.command('botright vsplit ~/.vim/util/scratch/scratch.todo')

@vimpy_command(mode='v')
def commentify_selection():
    """選択範囲をコメントにする。"""
    surround_text('"""','"""')

@vimpy_command()
def command_t(dir=""):
    """TextMate like fuzzy file finder"""
    if not dir: dir = vim.current_buffer_dir()
    vim.command("set timeoutlen=1000")
    vim.command("CommandT %s" % dir)

def vimbundle():
    """command-t with vim bundle dir"""
    command_t("~/.vim/bundle")

@vimpy_command()
def cheat():
    """select defunct's cheat-sheet"""
    command_t("~/.ch-sheets/")

def gem():
    """command-t with gem dir"""
    command_t("~/.rvm/gems/ruby-1.8.7-p302/gems")

@vimpy_command()
def scratch():
    """Open scratch"""
    vim.command("OpenScratch")

@vimpy_command()
def tips():
    """Open TIPS"""
    vim.command("TipsOpen")

@vimpy_command()
def tlist():
    """taglist Tlist"""
    vim.command("Tlist")

@vimpy_command()
def bp_edit():
    """Edit BestPractice"""
    vim.command("BPedit")

@vimpy_command(mode='v')
def bp_add():
    """add BestPractice"""
    vim.command('ruby $bp.bp_add')

@vimpy_command()
def bp_list():
    """List BestPractice"""
    vim.command("BPList")

@vimpy_command(mode='v')
def pythonify():
    """Enbed python to vim"""
    surround_text('python << ENDPYTHON','ENDPYTHON')

@vimpy_command(mode='v')
def rubyeval_insert():
    """Insert result of ruby eval"""
    vim.command('ruby $bp.insert_ruby_eval')

@vimpy_command(mode='v')
def rubyeval_print():
    """Print result of ruby eval"""
    vim.command('redir => g:py_b')
    vim.command('ruby $bp.print_ruby_eval')
    vim.command('redir END')
    return vim.eval('g:py_b')

# @vimpy_command(mode='n')
# def select_all_buffer():
  # """Select all buffer """
  # vim.normal("ggVG")

@vimpy_command(mode='nv')
def ruby_block_switch():
    """Toggle Ruby Block Style"""
    cr = ac_cmd.initial_range
    cmd = "%d,%dRubyBlockSwitch" % (cr.start+1, cr.end+1 )
    vim.command(cmd)

def methodize_selection():
    """選択範囲を method にする。"""
    surround_text('def','')

@vimpy_command(mode='nv')
def edit_tmp(file="/tmp/hogebuffer", how="split"):
    """open temporary file """
    vim.command("%s %s" % (how, file))
    vim.command("setlocal bufhidden=delete")
    vim.command("setlocal buftype=nofile")
    vim.command("setlocal noswapfile")
    vim.command("setlocal nobuflisted")
    vim.command("setlocal modifiable")

def analyze_code(how="vsplit"):
    tmp_xml = "/tmp/output.xml"
    tmp_py  = "/tmp/output.py"
    src = vim.current.buffer.name
    tchecker_cmd = "tchecker.py -o " + tmp_xml + "  " + src
    annot_cmd = "annot.py " + tmp_xml + " " + src
    os.system(tchecker_cmd)
    ret = os.popen(annot_cmd).read().split("\n")
    vim.command("%s %s" % (how, tmp_py))
    clear_buffer()
    vim.insert(0, ret)

@vimpy_command()
def clear_buffer():
    """Erase buffers contents"""
    del vim.current.buffer[:]

@vimpy_command()
def run_ipython():
    """Load current buffer to ipython"""
    cmd = "ruby $iterm.write('ipython %s')" % vim.current.buffer.name
    vim.command(cmd)

@vimpy_command()
def run_shell():
    """Start shell"""
    vim.command('Shell')

@vimpy_command()
def snippet_edit():
    """Edit SnipMate snippet"""
    vim.command('EditSnippets')

def snippet_system():
    """Edit system SnipMate snippet"""
    command_t("~/.vim/bundle/snipMate/snippets")

@vimpy_command()
def snippet_reload():
    """Reload Snippet"""
    vim.command('ReloadSnippets')
    return "Snippet Reloaded"

html_escape_table = {
    "&": "&amp;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    return "".join(html_escape_table.get(c,c) for c in text)

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s

@vimpy_command(mode='nv')
def nerd_tree():
    """NERDTree"""
    cmd = "NERDTree %s" % vim.current_buffer_dir()
    vim.command(cmd)

@vimpy_command(mode='nv')
def nerd_tree_close():
    """NERDTree Close"""
    vim.command('NERDTreeClose')

@vimpy_command(mode='nv')
def unite_mru():
    """Unite mru"""
    vim.command('Unite file_mru')

@vimpy_command(mode='n')
def vimwiki():
    """VimWiki Home"""
    vim.command('VimwikiGoHome')

def win_maximize_height():
    """Maximize window height"""
    vim.command('wincmd _')

def win_maximize_width():
    """Maximize window width"""
    vim.command('wincmd |')

def win_equalize():
    """Equqlize window width"""
    vim.command('wincmd =')

# def translate_english_to_japanese():
    # """選択範囲を日本語に翻訳"""
    # #[TODO] implement via google translate-api
    # def e2j(s):
        # s = s.replace("apple", "リンゴ")
        # s = s.replace("orange", "オレンジ")
        # return s
    # transform_selection(html_escape)

@vimpy_command(mode='nv')
def pwd():
    """Print working directory"""
    return vim.eval('getcwd()')

@vimpy_command()
def neco_enable():
    "Enable NeoCompleCache"
    vim.command('NeoComplCacheEnable')
    return "NeoCompleCache Enabled"

@vimpy_command()
def neco_disable():
    "Disable NeoCompleCache"
    try:
        vim.command('NeoComplCacheDisable')
        return "NeoCompleCache Disabled"
    except vim.error:
        return "NeoCompleCache Already Disabled"

@vimpy_command(mode='v')
def quick_run():
    """Quick Run"""
    cr = ac_cmd.initial_range
    vim.command("%d,%dQuickRun" % (cr.start+1, cr.end+1))

class ITerm(object):
    """docstring for ITerm"""
    def __init__(self):
        super(ITerm, self).__init__()
        self.app = appscript.app('iTerm')

    def write(self, cmd):
        self.app.current_terminal.sessions.write(text=cmd)

    def special_key(self, key, using=None):
        """send non printable key
        
        using is list of special key like:
        ['control_down', 'command_down', 'option_down']
        """
        sp_keys = [ getattr(appscript.k, sp_key) for sp_key in using if hasattr(appscript.k, sp_key) ]
        appscript.app('System Events').keystroke(key , using=sp_keys)


    def activate(self):
        self.app.activate()

iTerm=ITerm()
MacVim=appscript.app('MacVim')

@vimpy_command(mode='nv')
def py_koan():
    """Run python  'python2.7 contemplate_koans.py'"""
    iTerm.write('cd ~/Dropbox/dev/Python/python2')
    iTerm.write('python2.7 contemplate_koans.py')


######################################################################
# standard command source
######################################################################
ac_source = AnythingSource("cmd")
ac_source.candidate_n = [ (cmd.__name__, cmd.__doc__) for cmd in cmd_list if 'n' in cmd.mode ]
ac_source.candidate_v = [ (cmd.__name__, cmd.__doc__) for cmd in cmd_list if 'v' in cmd.mode ]
ac_source.action = lambda x,y: eval(x)()
ac_source.split_pattern = re.compile('_')

######################################################################
# command-t source
######################################################################
command_t_source = [ gem, vimbundle, cheat, snippet_system ]

ac_source_command_t = AnythingSource("com_t")
ac_source_command_t.candidate = [ (cmd.__name__, cmd.__doc__) for cmd in command_t_source ]
ac_source_command_t.action = lambda x,y: eval(x)()
ac_source_command_t.split_pattern = re.compile('_')

ac_cmd = Anything("ac_cmd", ac_source, ac_source_command_t)

