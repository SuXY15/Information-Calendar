# coding=utf-8
import os, sys
import numpy as np
from util import *
from BeautifulSoup import BeautifulSoup

# configration
ext_path = configReader(section='extract',option='ext_path')
pos_page = configReader(section='path',option='pos_page')
pos_post = configReader(section='post',option='pos_post')
num_tags = configReader(section='post',option='num_tags')

if __name__ == "__main__" :
    # preparation
    tic()
    rec_page = recordReader(configReader(section='record',option='rec_page'))
    
    # handle every page in record
    for i in range(len(rec_page)):
        pageFileName = pos_page+'/'+str(rec_page[i][1]).replace('/','_')+'.html'
        postFileName = pos_post+str(rec_page[i][0]).replace('.','-')+'-'+str(rec_page[i][1]).replace('/','_')+'.html'
        url_info = os.path.split(rec_page[i][1])[0]
        printInfo("Analyzing and post page: %s"%pageFileName)
        # load page
        text = dataReader(pageFileName)
        # change url of images to be correct
        try:
            soup = BeautifulSoup(text)
            text = soup.prettify()
            if soup.img:
                for t in soup.findAll('img'):
                    s = BeautifulSoup(str(t))
                    src = s.img['src']
                    s.img['src'] = url_info+src if src[0:4]!='http' else src
                    text = text.replace(str(t), s.prettify())
            text = myEncoding(text)
        except:
            RaiseErr('display', pageFileName)
        # setting of post
        rec_ext= recordReader(ext_path+str(rec_page[i][1]).replace('/','_')+"_ext.txt")
        layout = "layout:      post\n"
        title  = "title:       %s\n"%rec_page[i][2]
        excerpt= "excerpt:     <a href="+rec_page[i][1]+">%s</a>\n"%rec_page[i][1]
        tags   = "tags:\n"
        try:
            for j in range(int(num_tags)):
                tags += "  %s\n"%rec_ext[j][0]
        except:
            pass
        m_date = "modify_date: %s\n"%str(rec_page[i][0]).replace('.','-')
        header = "---\n"+layout+title+excerpt+tags+m_date+"---\n"
        # write post
        try:
            dataWriter(header+text, postFileName)
        except:
            RaiseErr('rit_pos', pageFileName)
    
    # error output
    OutputErr()
    toc()
    