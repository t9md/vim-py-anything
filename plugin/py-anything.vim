let s:dirname = expand('<sfile>:h')
let s:basedir = fnamemodify(s:dirname, ':h') . '/python'

python << ENDPYTHON
import sys
import vim
sys.path[0:1] = [vim.eval('s:basedir')]
from ac_source_cmd import *
from ac_source_buffer import *
ac_src_dict={0:ac_src_cmd, 1:ac_src_command_t, 2:ac_src_buffer }
ENDPYTHON
