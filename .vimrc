autocmd FileType tex set iskeyword=@,48-57,_,-,192-255,\:
autocmd FileType tex set dictionary=bibkeys.lst,labels.lst

" Skim sync
autocmd FileType tex nnoremap <Leader>s :w<CR>:silent !/Applications/Skim.app/Contents/SharedSupport/displayline -g <C-r>=line('.')<CR> diss.pdf %<CR><C-l>
