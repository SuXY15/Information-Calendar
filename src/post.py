# coding=utf-8
import os, sys
import numpy as np
from util import *
from HTMLParser import HTMLParser

pos_info = configReader(section='list',option='pos_info')
pos_page = configReader(section='path',option='pos_page')
pos_post = configReader(section='post',option='pos_post')
ext_path = configReader(section='extract',option='ext_path')

pos_page = os.path.split(pos_page)[0]

# postParser: output the post #
class PostParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.pages = {'images':[],'encoding':None}
        self.flag = True

    def handle_starttag(self,tag,attrs):
        def _attr(attrlist,attrname):
            for each in attrlist:
                if attrname == each[0]:
                    return each[1]
            return None

        if tag=='meta':
            content = _attr(attrs,'content')
            if content.find('charset')!=-1:
                self.pages['encoding'] = content[content.find('charset')+len('charset='):-1]+content[-1]
        if tag=='img':
            self.pages['images'].append(pos_info+_attr(attrs,'src'))

if __name__ == "__main__" :
    # preparation
    tic()
    for f in getFileList(pos_page, suffix='.html'):
        printInfo("Analyzing and post page: %s"%f)
        text = dataReader(pos_page+'/'+f)
        try:
            parser = PostParser()
            parser.feed(str(text))
            parser.close()
            text = myEncoding(text,parser.pages['encoding'])
        except:
            RaiseErr('display', pos_page+'/'+f)
        header = "---\nlayout:      post\ntitle:       %s \nexcerpt:      None\ntags: \n  - None\nmodify_date: 2018-04-16\n---\n"%f
        try:
            dataWriter(header+text,pos_post+"2018-05-28-"+os.path.split(f)[1])
        except:
            RaiseErr('rit_pos', pos_page+'/'+f)
    
    # error output
    OutputErr()
    toc()
    