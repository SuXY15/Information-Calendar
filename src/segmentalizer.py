# coding=utf-8
import os, sys, jieba, thulac
from util import *

pos_text = configReader(section='path', option='pos_text')
pos_erro = configReader(section='path', option='pos_erro')
seg_path = configReader(section='segment', option='seg_path')
seg_mthd = cleanWord(configReader(section='segment', option='seg_mthd'))

# segmentalize: divide words
def segmentalize(fileName, cutter):
    filePath = pos_text
    print "Segmentalizing: "+filePath+fileName
    try:
        text = myEncoding(dataReader(filePath+fileName,'r+'))
    except:
        RaiseErr('segment', filePath+fileName)
        text = dataReader(filePath+fileName,'r+')

    # default segmentalize
    try:
        seg_list = cutter(text)
    except:
        seg_list = []
        RaiseErr('segment', filePath+fileName)
    if seg_mthd == 'jieba':
        seg_list = [cleanWord(seg) for seg in seg_list]
    if seg_mthd == 'thulac':
        seg_list = [cleanWord(seg[0]) for seg in seg_list]
    seg_list = [seg+' ' for seg in seg_list if seg!='']

    # save
    segfName = seg_path+"/"+os.path.splitext(fileName)[0]+"_seg.txt"
    try:
        dataWriter(seg_list, segfName, 'w')
    except:
        RaiseErr('rit_seg', segfName)
    return segfName

if __name__=='__main__':
    # preparation
    tic()
    checkPath(seg_path)
    rec_page = recordReader(configReader(section='record',option='rec_page'))
    rec_sege = recordReader(configReader(section='record',option='rec_sege'))
    hrefs = [ri[1] for ri in rec_sege]

    if seg_mthd == 'jieba':
        cutter = jieba.cut
    elif seg_mthd == 'thulac':
        thul = thulac.thulac(seg_only=True).cut
        cutter = thul

    # handle
    for i in range(len(rec_page)):
        f = str(rec_page[i][1]).replace('/','_')+'.txt'
        if f not in hrefs:
            segmentalize(f, cutter)
            rec_sege.append([rec_page[i][0],f,rec_page[i][2]])

    recordWriter(configReader(section='record',option='rec_sege'),rec_sege)
    # error output
    OutputErr()
    toc()
