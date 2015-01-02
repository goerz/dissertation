set ft=tex
set iskeyword=@,48-57,_,-,192-255,\:
set dictionary=bibkeys.lst,labels.lst

" Skim sync
nnoremap <Leader>s :w<CR>:silent !/Applications/Skim.app/Contents/SharedSupport/displayline -g <C-r>=line('.')<CR> diss.pdf %<CR><C-l>
