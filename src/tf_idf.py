# coding=utf-8
import os, sys
import numpy as np
from util import *

from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# TF-IDF algorithm
def tf_idf(pos_seg='./segfile/', pos_ext='./tfidffile'):
    # read corpus
    fileList = getFileList(pos_seg)
    corpus = [dataReader(pos_seg+f,'r+') for f in fileList]

    # transform by TF-IDF algorithm
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    
    word = vectorizer.get_feature_names() # key words of all texts
    weight = tfidf.toarray()              # tf-idf matrix

    # save extracted file
    checkPath(pos_ext)
    for i in range(len(weight)):
        fileName = pos_ext+os.path.splitext(fileList[i])[0][0:-4]+'_ext.txt'
        print "Writing tf-idf extraction: %s"%fileName
        # sort and output only not-zero weights
        index = np.argsort(-weight[i])
        data = ["%-20s %-10.8f\n"%(word[index[j]], weight[i][index[j]]) for j in range(len(word)) if weight[i][index[j]]!=0]
        try:
            dataWriter(data, fileName, 'w')
        except:
            RaiseErr('rit_ext',fileName)

if __name__ == "__main__" :
    # preparation
    tic()
    pos_seg = configReader(section='segment', option='pos_seg')
    pos_ext = configReader(section='extract', option='pos_ext')

    # handle
    tf_idf(pos_seg, pos_ext)

    # error output
    OutputErr()
    toc()
    