# coding=utf-8
import os, sys
import numpy as np
from util import *
from BeautifulSoup import BeautifulSoup

# configration
ext_path = configReader(section='extract',option='ext_path')
rec_page = configReader(section='record',option='rec_page')
pos_page = configReader(section='path',option='pos_page')
pos_post = configReader(section='post',option='pos_post')
num_tags = configReader(section='post',option='num_tags')
num_tags = int(num_tags)
rub_info = ["<!-–[if IE]>","<![endif]–->",]

if __name__ == "__main__" :
    # preparation
    tic()
    rec_page = recordReader(rec_page)
    
    # handle every page in record
    for i in range(len(rec_page)):
        # load value
        date,href,title = rec_page[i][0],rec_page[i][1],rec_page[i][2]
        pageFileName = pos_page+'/'+http2str(href)+'.html'
        postFileName = pos_post+date.replace('.','-')+'-'+http2str(href)+'.html'
        url_info = os.path.split(rec_page[i][1])[0]
        print "Analyzing and posting page: %s"%pageFileName

        # load page
        text = dataReader(pageFileName)

        # clear rub msg
        for rub in rub_info:
            if text.find(rub)!=-1:
                text = text.replace(rub,"<!-- "+rub+" -->")

        try:
            # add url link
            soup = BeautifulSoup(text)
            link = BeautifulSoup("<div><a href=%s>%s</a></div>\n"%(rec_page[i][1],rec_page[i][1]))
            soup.body.div.insert(0,link)
            
            # replace img with pre-url
            text = soup.prettify()
            soup = BeautifulSoup(text)
            if soup.img!=None:
                for imgStr in soup.findAll('img'):
                    imgTag = BeautifulSoup(str(imgStr))
                    imgSrc = imgTag.img['src']
                    imgTag.img['src'] = url_info+imgSrc if imgSrc[0:4]!='http' else imgSrc
                    text = text.replace(str(imgStr), imgTag.prettify())
        except:
            RaiseErr('display', "%30s %100s"%(title, pageFileName))
        # setting of post
        rec_ext= recordReader(ext_path+http2str(href)+"_ext.txt")
        layout = "layout:      post\n"
        title  = "title:       %s\n"%title
        excerpt= "excerpt:     <a href="+href+">%s</a>\n"%href
        tags   = "tags:\n"
        try:
            for j in range(num_tags):
                tags += "  %s\n"%rec_ext[j][0]
        except:
            pass
        m_date = "modify_date: %s\n"%date.replace('.','-')
        header = "---\n"+layout+title+excerpt+tags+m_date+"---\n"
        # write post
        try:
            dataWriter(header+myEncoding(text), postFileName)
        except:
            RaiseErr('rit_pos', pageFileName)

    # error output
    OutputErr()
    toc()
    