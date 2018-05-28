#coding=utf-8
import os, sys, time
import re, urllib2
from util import *
from HTMLParser import HTMLParser

# configuratio of list
conf_list = dict(configReader(section='list'))
list_arange = range(int(conf_list['beg']),int(conf_list['end']))
url_info = conf_list['url_info'];
url_list = conf_list['url_list'];

# configuratio of path
conf_path = dict(configReader(section='path'))
pos_list = conf_path['pos_list'];checkPath(pos_list)
pos_page = conf_path['pos_page'];checkPath(pos_page)
pos_text = conf_path['pos_text'];checkPath(pos_text)

# crawler: crawl a page and save to fout #
def Crawler(url, key, fout=''):
    print 'Getting: '+url
    try:
        if key=='urllib':
            return urllib2.urlopen(url).read()
        elif key=='axel':
            cmd = 'axel -n 5 '+str(url)+' --output='+str(fout)
            return os.popen(cmd)
    except:
        RaiseErr('getting',key+" "+url)

# listParser: extract pages' link #
class ListParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.pages = []
        self.page = None

    # list info extractor
    def handle_starttag(self,tag,attrs):
        def _attr(attrlist,attrname):
            for each in attrlist:
                if attrname == each[0]:
                    return each[1]
            return None
        # tag: em,   the start signal of list in jiaowugonggao
        if tag == 'em' and _attr(attrs,'class')=='red fb mr5':
            self.page = {"href":None,'title':None}
        # tag: a,    the url
        if tag == 'a' and self.page != None:
            self.page['href'] = _attr(attrs,'href').replace(' ','')
            if self.page['href'][0:6]=='/node/':
                self.page['href']=url_info+self.page['href']
        # tag: time, the time
        if tag == 'time' and self.page != None:
            self.page['time'] = _attr(attrs,'datetime').replace(' ','')
        # tag: li,   the end signal of list
        if tag == 'li' and self.page != None:
            self.page['content'] = Crawler(self.page['href'],'urllib')
            self.pages.append(self.page)
            self.page = None

    def handle_data(self,data):
        if self.page!=None and self.page['href']!=None and self.page['title']==None:
            self.page['title']=data.replace(' ','')

# pageParser: extracting pages' content #
class PageParser(HTMLParser):
    def __init__(self,url=''):
        HTMLParser.__init__(self)
        self.pages = {'content':'','encoding':None}
        self.url = os.path.split(url)[0]
        self.flag = True

    # page content extractor
    def handle_starttag(self,tag,attrs):
        def _attr(attrlist,attrname):
            for each in attrlist:
                if attrname == each[0]:
                    return each[1]
            return None
        # tag: meta,  contains charset encoding
        if tag=='meta':
            content = _attr(attrs,'content')
            if content.find('charset')!=-1:
                self.pages['encoding'] = content[content.find('charset')+len('charset='):-1]+content[-1]
        # tag: script or style, useless in text
        if tag=='SCRIPT' or tag=='script' or tag=='style':
            self.flag = False
        # tag: img,  need to handle
        if tag=='img':
            src = _attr(attrs,'src')
            src = self.url+src if src[0:4]!='http' else src
            self.pages['content'] += '['+src+']'

    def handle_endtag(self,tag):
        if tag=='SCRIPT' or tag=='script' or tag=='style':
            self.flag = True

    def handle_data(self,data):
        self.pages['content'] += str([data if self.flag else ''][0])

# textParser: handle msg in text #
def textParser(text, parser):    
    parser.feed(str(text))
    parser.close()
    return parser.pages

# fileParser: handle msg in file #
def fileParser(fileName, parser):
    fin = open(fileName,'r')
    text = textParser(fin.read(),parser)
    fin.close()
    return text

# main #
if __name__=='__main__':
    # preparation
    tic()

    # crawling list
    printInfo("Getting List From %s"%url_list)
    for index in list_arange:
        listFileName = pos_list+(url_list%index).replace("/",'_')+'.html'
        Crawler(url_list%index, 'axel', listFileName)

    # load record
    rec_page = recordReader(configReader(section='record',option='rec_page'))

    # analyze list and crawling pages
    for index in list_arange:
        printInfo("Analyzing List %4d and Crawling pages"%index)
        listFileName = pos_list+(url_list%index).replace("/",'_')+'.html'
        
        # analyze list and crawling pages
        try:
            pages = fileParser(listFileName, parser=ListParser())
        except:
            RaiseErr('parsing', listFileName)

        # loop to handle pages one by one
        hrefs = [ri[1] for ri in rec_page]
        for i in range(len(pages)):
            page = pages[i];
            href = page['href']
            content = page['content']
            pageFileName = pos_page+str(href).replace('/','_')+'.html'
            textFileName = pos_text+str(href).replace('/','_')+'.txt'
            
            if href not in hrefs:
                # save pages
                try:
                    dataWriter(content, pageFileName)
                except:
                    RaiseErr('writing', pageFileName)
                
                # analyze page
                try:
                    temp = textParser(content, parser=PageParser(url=href))
                    text = temp['content'].replace('\r\n','\n');
                    encoding = temp['encoding']
                    text = cleanText(myEncoding(text,encoding))
                except:
                    RaiseErr('parsing', pageFileName+' '+encoding)
                    text = cleanText(text)

                # save extracted text
                try:
                    dataWriter(text, textFileName)
                except:
                    RaiseErr('writing', textFileName)
                rec_page.append([page['time'],page['href'],page['title']])
    
    # save new record
    recordWriter(configReader(section='record',option='rec_page'),rec_page)

    # error output
    OutputErr()
    toc()
