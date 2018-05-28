#coding=utf-8
import os, sys, time
import re, urllib2
from util import *
from HTMLParser import HTMLParser


config_list = dict(configReader(section='list'))
list_arange = range(int(config_list['beg']),int(config_list['end']))
pos_info = config_list['pos_info'];
list_url = config_list['list_url'];

config_path = dict(configReader(section='path'))
pos_list = config_path['pos_list'];checkPath(os.path.split(pos_list)[0])
pos_page = config_path['pos_page'];checkPath(os.path.split(pos_page)[0])
pos_text = config_path['pos_text'];checkPath(os.path.split(pos_text)[0])
pos_erro = config_path['pos_erro'];checkPath(os.path.split(pos_erro)[0])

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

    def handle_starttag(self,tag,attrs):
        def _attr(attrlist,attrname):
            for each in attrlist:
                if attrname == each[0]:
                    return each[1]
            return None
        # list info extractor
        if tag == 'em' and _attr(attrs,'class')=='red fb mr5':
            self.page = {"href":None,'title':None}
        if tag == 'a' and self.page != None:
            self.page['href'] = _attr(attrs,'href')
            if self.page['href'][0:6]=='/node/':
                self.page['href']=pos_info+self.page['href']
        if tag == 'time' and self.page != None:
            self.page['time'] = _attr(attrs,'datetime')
        if tag == 'li' and self.page != None:
            self.page['content'] = Crawler(self.page['href'],'urllib')
            self.pages.append(self.page)
            self.page = None

    def handle_data(self,data):
        if self.page!=None and self.page['href']!=None and self.page['title']==None:
            self.page['title']=data

# pageParser: extracting pages' content #
class PageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.pages = {'content':'','encoding':None}
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
        if tag=='SCRIPT' or tag=='script' or tag=='style':
            self.flag = False
        if tag=='img':
            self.pages['content'] += pos_info+str(attrs)


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
    printInfo("Getting List From %s"%list_url)
    for index in list_arange:
        Crawler(list_url%index, 'axel', pos_list%index)

    # analyze list and crawling pages
    for index in list_arange:
        printInfo("Analyzing List %4d and Crawling pages"%index)
        # analyze list and crawling pages
        try:
            pages = fileParser(pos_list%index, parser=ListParser())
        except:
            RaiseErr('parsing', pos_list%index)

        # loop to handle pages one by one
        for i in range(len(pages)):
            page = pages[i]
            # save pages
            try:
                dataWriter(page['content'], pos_page%(index,i))
            except:
                RaiseErr('writing', pos_page%(index,i))
            
            # analyze page
            try:
                page = textParser(page['content'], parser=PageParser())
                text = page['content'].replace('\r\n','\n');
                encoding = page['encoding']
                text = cleanText(myEncoding(text,encoding))
            except:
                RaiseErr('parsing', pos_page%(index,i)+' '+encoding)
                text = cleanText(text)

            # save extracted text
            try:
                dataWriter(text, pos_text%(index,i))
            except:
                RaiseErr('writing', pos_text%(index,i))

    # error output
    OutputErr()
    toc()
