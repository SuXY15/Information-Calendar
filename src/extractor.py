# coding=utf-8
import os, sys
import numpy as np
from util import *
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# configuration
seg_path = configReader(section='segment', option='seg_path')
ext_path = configReader(section='extract', option='ext_path')
ext_mthd = configReader(section='extract', option='ext_mthd')

# TF-IDF algorithm
def tf_idf(seg_path='./segfile/', pos_ext='./tfidffile'):
    # read corpus
    fileList = getFileList(seg_path)
    corpus = [dataReader(seg_path+f,'r+') for f in fileList]

    # transform by TF-IDF algorithm
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    word = vectorizer.get_feature_names() # key words of all texts
    weight = tfidf.toarray()              # tf-idf matrix

    # save extracted file
    checkPath(ext_path)
    for i in range(len(weight)):
        fileName = ext_path+os.path.splitext(fileList[i])[0][0:-4]+'_ext.txt'
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

    # handle
    if ext_mthd=='tf_idf':
        tf_idf(seg_path, ext_path)

    # error output
    OutputErr()
    toc()
    