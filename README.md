vim-py-anything
=======================
This is vim's plugin which aims to similar functionality to Emacs's anything.
This plugin is completely written in python.

Main purpose to create this plugin is to teach me python programming language.
So, feature is greatly specific for my development environment.

This plugin require +python feature.

NOTE: this plugin is very very alpha state.

Setting example
----------------------------------
# .vimrc
    nnoremap <D-j> :python anything.start()<CR>
    vnoremap <D-j> :python anything.start('v')<CR>
    nnoremap <C-n> :python ac_buffer.start()<CR>
    vnoremap <C-n> :python ac_buffer.start()<CR>

# directly launch command without using anything window.
    au BufNewFile,BufReadPost about_*.py nnoremap <buffer> <D-r> :python ac_cmd.run(py_koan)<CR>

anything_source_cmd example
----------------------------------
If you want add the new command to anything_source_cmd.
See following example.

    @vimpy_command(mode='v')
    def this_is_new_cmd(arg1, arg2):
        """This doc string is shown in anytiing window"""

        "you can read user's input by vim.prompt"
        if not header: header = vim.prompt("header? :")
        if not footer: footer = vim.prompt("footer? :")

        " you can use ac_cmd.initial_range to get range"
        cr = anything.initial_range
        new_text = [header] + cr[:] + [footer]
        cr[:] = None
        vim.insert(cr.start,new_text)

Special Tanks
----------------------------------
### [ Command-t ]( https://github.com/wincent/Command-T )

User interface and architecture is greately inspired and bollwed from command-t which is also derived from inspired by LustiExplorer.

### [ vimilicious ]( https://github.com/remi/vimilicious )

