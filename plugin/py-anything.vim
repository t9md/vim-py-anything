let s:dirname = expand('<sfile>:h')
let s:basedir = fnamemodify(s:dirname, ':h') . '/python'

python << ENDPYTHON
import sys
import vim
print vim.eval('s:basedir')
sys.path[0:1] = [vim.eval('s:basedir')]
from ac_source_cmd import *
from ac_source_buffer import *
ENDPYTHON
