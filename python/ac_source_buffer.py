# -*- coding: utf8 -*-
# import vim
# import sys
import re
import os
from   anything import *


__all__ = ( 'ac_src_buffer', )
# print anything.source.split_pattern
######################################################################
# buffer source
######################################################################
ac_src_buffer = AnythingSource("buffer")

exclude_buffer_ptns = [
    '/Users/taqumd/NERD_tree' ,
    '__Tag_List__',
    'anything-buffer',
    '\*unite\*',
    '\[.*\]',
    'None',
]

def __buffer_should_exclude(x):
    for ptn in exclude_buffer_ptns:
        if re.search(ptn, x): return True
    return False

ac_src_buffer.volatile = True
ac_src_buffer.action = lambda x,y: vim.command("edit %s" % y.split()[-1] )
ac_src_buffer.prepare_candidate = lambda: [ (os.path.basename(b.name), b.name) for b in vim.buffers
        if b.name and not __buffer_should_exclude(b.name) ]

ac_src_buffer.split_pattern = re.compile('\.|_')
# ac_buffer = Anything("ac_buffer", ac_source_buffer)
