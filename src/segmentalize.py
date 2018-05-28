# coding=utf-8
import os, sys, jieba, thulac
from util import *

pos_text = os.path.split(configReader(section='path', option='pos_text'))[0]+'/'
pos_erro = configReader(section='path', option='pos_erro')
pos_seg  = configReader(section='segment', option='pos_seg')
method   = cleanWord(configReader(section='segment', option='method'))

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
    if method == 'jieba':
        seg_list = [cleanWord(seg) for seg in seg_list]
    if method == 'thulac':
        seg_list = [cleanWord(seg[0]) for seg in seg_list]
    seg_list = [seg+' ' for seg in seg_list if seg!='']

    # save
    segfName = pos_seg+"/"+os.path.splitext(fileName)[0]+"_seg.txt"
    try:
        dataWriter(seg_list, segfName, 'w')
    except:
        RaiseErr('rit_seg', segfName)
    return segfName

if __name__=='__main__':
    # preparation
    tic()
    checkPath(pos_seg)

    # handle
    if method == 'jieba':
        cutter = jieba.cut
    elif method == 'thulac':
        thul = thulac.thulac(seg_only=True)
        cutter = thul.cut
    segfList = [segmentalize(f, cutter) for f in getFileList(pos_text)]

    # error output
    OutputErr()
    toc()
