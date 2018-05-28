# coding=utf-8
import os, sys
import numpy as np
from util import *
from BeautifulSoup import BeautifulSoup

ext_path = configReader(section='extract',option='ext_path')
pos_page = configReader(section='path',option='pos_page')
pos_post = configReader(section='post',option='pos_post')
num_tags = configReader(section='post',option='num_tags')

if __name__ == "__main__" :
    # preparation
    tic()
    rec_page = recordReader(configReader(section='record',option='rec_page'))
    
    for i in range(len(rec_page)):
        f = pos_page+'/'+str(rec_page[i][1]).replace('/','_')+'.html'
        printInfo("Analyzing and post page: %s"%f)
        text = dataReader(f)
        try:
            soup = BeautifulSoup(text)
            if soup.img:
                src = soup.img['src']
                url_info = os.path.split(rec_page[i][1])[0]
                soup.img['src'] = url_info+src if src[0:4]!='http' else src
            text = myEncoding(soup.prettify())
        except:
            RaiseErr('display', f)
        layout = "layout:      post\n"
        title  = "title:       %s\n"%rec_page[i][2]
        excerpt= "excerpt:     <a href="+rec_page[i][1]+">%s</a>\n"%rec_page[i][1]
        rec_ext= recordReader(ext_path+str(rec_page[i][1]).replace('/','_')+"_ext.txt")
        tags   = "tags:\n"
        try:
            for j in range(int(num_tags)):
                  tags += "  %s\n"%rec_ext[j][0]
        except:
            pass
        m_date = "modify_date: %s\n"%str(rec_page[i][0]).replace('.','-')
        header = "---\n"+layout+title+excerpt+tags+m_date+"---\n"
        try:
            dataWriter(header+text,pos_post+str(rec_page[i][0]).replace('.','-')+'-'+str(rec_page[i][1]).replace('/','_')+'.html')
        except:
            RaiseErr('rit_pos', f)
    
    # error output
    OutputErr()
    toc()
    