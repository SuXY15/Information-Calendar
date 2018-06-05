# coding=utf-8
import os, sys
import numpy as np
import jieba
import jieba.analyse
import lda, codecs, collections

from util import *
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# configuration
seg_path = configReader(section='segment', option='seg_path')
ext_path = configReader(section='extract', option='ext_path')
ext_mthd = configReader(section='extract', option='ext_mthd')
rec_extr = configReader(section='record', option='rec_extr')

# TF-IDF algorithm
def tf_idf():
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

def textRank():
    # read corpus
    fileList = getFileList(seg_path)
    corpus = [dataReader(seg_path+f,'r+') for f in fileList]

    # save extracted file
    for i in range(len(corpus)):
        fileName = ext_path+os.path.splitext(fileList[i])[0][0:-4]+'_ext.txt'
        keywords = jieba.analyse.textrank(corpus[i], topK=100, withWeight=True)
        print "Writing textRank extraction: %s"%fileName
        # sort and output only not-zero weights
        data = ["%-20s %-10.8f\n"%(key[0], key[1]) for key in keywords]
        try:
            dataWriter(data, fileName, 'w')
        except:
            RaiseErr('rit_ext',fileName)

def basicLDA(X):
    # preparation
    n_iter = int(configReader(section='extract', option='n_iter'))
    n_topics = int(configReader(section='extract', option='n_topics'))
    random_state = int(configReader(section='extract', option='random_state'))

    fileList = getFileList(seg_path)

    # train
    model = lda.LDA(n_topics = n_topics, n_iter = n_iter, random_state = random_state)
    model.fit(X)
    
    doc_topic = model.doc_topic_
    topic_word = model.topic_word_

    # write extraction record
    print "Writing LDATFIDF record: %s"%rec_extr
    with open(rec_extr,'w') as f:
        try:
            for i, topic_dist in enumerate(topic_word):
                topic_words = np.array(wordList)[np.argsort(topic_dist)][:-(n_topics+1):-1]
                f.write("%d\t%s\n"%(i,' '.join(topic_words)))
        except:
            RaiseErr('rit_ext',rec_extr)

    # write type division
    for i in range(len(fileList)):
        fileName = ext_path+os.path.splitext(fileList[i])[0][0:-4]+'_ext.txt'
        print "Writing LDATFIDF_topic extraction: %s"%fileName
        topic_most_pr = doc_topic[i].argmax()
        try:
            dataWriter(["type%d"%topic_most_pr], fileName, 'w')
        except:
            RaiseErr('rit_ext',fileName)

def myLDA():
    fileList = getFileList(seg_path)
    corpus = [dataReader(seg_path+f,'r+') for f in fileList]

    # punction
    punc = ("\[\]\{\}\"\'"+",./;':-=_+)(*&^%$#@!~`！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾\
            ＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.").decode("utf-8")

    # get word matrix
    wordSet = set()  
    for index in range(len(corpus)):  
        corpus[index] = re.sub(ur"([%s])+"%punc, "", corpus[index].decode("utf-8"))
        corpus[index] = re.sub("[A-Za-z0-9\!\%\[\]\,\。]", "", corpus[index])
        lineList = corpus[index].split(' ')
        for i in range(len(lineList)):
            wordSet.add(lineList[i].strip())
    wordList = list(wordSet)
    
    wordMatrix = []
    for index in range(len(corpus)):  
        docWords = corpus[index].strip().split(' ')  
        diction = collections.Counter(docWords)  
        keys = list(diction.keys())  
        wordMatrix.append([diction[w] if w in keys else 0 for w in wordList])  
    X = np.array(wordMatrix)

    basicLDA(X)

def LDATFIDF():
    # read corpus
    fileList = getFileList(seg_path)
    corpus = [dataReader(seg_path+f,'r+') for f in fileList]

    # punction
    punc = ("\[\]\{\}\"\'"+",./;':-=_+)(*&^%$#@!~`！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾\
            ＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.").decode("utf-8")

    # replace by ???
    for index in range(len(corpus)):  
        corpus[index] = re.sub(ur"([%s])+"%punc, "", corpus[index].decode("utf-8"))
        corpus[index] = re.sub("[A-Za-z0-9\!\%\[\]\,\。]", "", corpus[index])

    # transform by TF-IDF algorithm
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    wordList = vectorizer.get_feature_names() # key words of all texts
    weight = tfidf.toarray()                  # tf-idf matrix
    X = (np.log(np.array(weight) / weight.mean() + 1) * 2).astype(int)
    
    basicLDA(X)

# def word2Vec(seg_path='./segfile/', pos_ext='./extfile'):

def pynlpir():
    import pynlpir
    # read corpus
    pos_text = configReader(section='path', option='pos_text')
    fileList = getFileList(pos_text)
    corpus = [dataReader(pos_text+f,'r+') for f in fileList]
    
    # pynlpir open
    pynlpir.open()
    for i in range(len(corpus)):
        fileName = ext_path+os.path.splitext(fileList[i])[0]+'_ext.txt'
        print "Writing pynlpir extraction: %s"%fileName
        try:
            keys = pynlpir.get_key_words(corpus[i], weighted=True)
        except:
            RaiseErr('extract',fileName)
        # output
        data = ["%-20s %-10.8f\n"%(key[0], key[1]) for key in keys]
        try:
            dataWriter(data, fileName, 'w')
        except:
            RaiseErr('rit_ext',fileName)
    pynlpir.close()

if __name__ == "__main__" :
    # preparation
    tic()

    # handle
    checkPath(ext_path)
    lookup(ext_mthd, globals())()
    
    # error output
    OutputErr()
    toc()
    