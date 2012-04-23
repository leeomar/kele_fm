#/bin/python
## -*- coding: utf-8 -*-
import codecs
from pymmseg import mmseg

class Categorizer(object):
    DEFAULT_CATEGORY = 0
    
    def load(self, category_file, tag_file, dic_file):
        self.category_map = {}
        #f = file(configue_file) 
        f = codecs.open(category_file, 'r', 'utf-8')
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            fields = line.split(":")
            #print type(fields[0]), type(fields[0].encode('utf-8'))
            key = fields[0].encode('utf-8')
            self.category_map[key] = int(fields[1])
        f.close()
        print "load %s" % category_file
        
        self.tags = []
        f = codecs.open(tag_file, 'r', 'utf-8')
        while True:
            line = f.readline().encode('utf-8')
            if len(line) == 0:
                break
            self.tags.append(line.strip())

        #mmseg.dict_load_defaults()
        mmseg.dict_load_words(dic_file)
        print "load %s" % tag_file

    def get_category(self, text):
        #print type(title)
        algor = mmseg.Algorithm(text)
        cat_id = Categorizer.DEFAULT_CATEGORY 
        for tok in algor:
            tok = str(tok)
            tmp_id = self.category_map.get(tok, -2)
            if tmp_id > cat_id:
                cat_id = tmp_id
        return cat_id  

    def get_tag(self, text):
        algor = mmseg.Algorithm(text)
        result = []
        for tok in algor:
            tok = str(tok)
            if tok in self.tags: 
                result.append(tok) 
        return ' '.join(result)

if __name__ == "__main__":
    cgr = Categorizer()
    cgr.load('category.cfg', 'tags.cfg', 'words.dic')
    text = 'kappa迷你内衣运动装学院风'
    print cgr.get_category(text)
    print cgr.get_tag(text)
