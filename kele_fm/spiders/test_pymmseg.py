#/bin/python
#coding:utf-8

from pymmseg import mmseg
 
mmseg.dict_load_defaults()
mmseg.dict_load_words('words.dic')
text = "kappa运动装迷你背心" 
algor = mmseg.Algorithm(text)
for tok in algor:
    print '%s [%d..%d]' % (tok.text, tok.start, tok.end)
