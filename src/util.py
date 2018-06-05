# coding=utf-8
import os, sys, time
import re, chardet, ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')

# global setting
global time_0
time_0 = None

global ErrorMsg
ErrorMsg = {
    'getting':[], 'parsing':[], 'writing':[],
    'segment':[], 'rit_seg':[],
    'extract':[], 'rit_ext':[],
    'display':[], 'rit_pos':[],
}

# tic: set time init
def tic():
    global time_0
    time_0 = time.time()
    return time_0

# toc: time after init
def toc():
    global time_0
    print 'toc: %-8.3fs'%(time.time()-time_0) if time_0!=None else 'tic: %-8.3fs'%tic()

# printInfo: print infomation with partition #
def printInfo(msg):
    print '\n-----------------\n'+str(msg)+'\n-----------------\n'

# getFileList: get file list of path #
def getFileList(path, suffix='.txt'):
    return sorted([f for f in os.listdir(path) if os.path.splitext(f)[1]==suffix])

# checkPath: check if path exists, if not, build it #
def checkPath(path):
    if not os.path.exists(path):
        os.mkdir(path)

# myEncoding: set encoding to utf-8 #
def myEncoding(text,encoding=None):
    if encoding==None:
        encoding = chardet.detect(text)['encoding']
    return text.decode(encoding).encode('utf-8')

# cleanWord: clean for word, throw '\n' and ' ' #
def cleanWord(word):
    return re.sub(r'\n{1,}| {2,}', ' ', ''.join(word.split()))
    
# cleanText: clean unnecessary msg in text #
def cleanText(text):
    return re.sub(r' \n|\n |\n{1,}', '\n', re.sub(r'\t| {2,}', '', text))

# dataReader: read a file and return it's content
def dataReader(fin, tp='r'):
    with open(fin, tp) as f:
        data = f.read()
        f.close()
        return data

# dataWriter: write data to fout #
def dataWriter(data, fout, tp='w'):
    with open(fout, tp) as f:
        for line in data:
            f.writelines(line)
        f.close()

# recordReader: read record.txt
def recordReader(rec_file):
    if not os.path.exists(rec_file):
        os.popen('touch '+rec_file)
    record = []; recorder = open(rec_file,'r')
    try:
        for line in recorder:
            ri = re.split(' ',line); ri = sorted(set(ri),key=ri.index)
            ri = [rii.replace('\n','') for rii in ri]+['']; ri.remove('')
            record.append(ri)
    except:
        pass
    recorder.close()
    return record

def recordWriter(rec_file, record):
    record.sort(key=lambda ri:-int(ri[0][0:4])*366-int(ri[0][5:7])*31-int(ri[0][8:10]))
    recorder = open(rec_file,'w')
    for ri in record:
        recorder.writelines("%-10s  %-90s %-50s\n"%(ri[0],ri[1],ri[2]))
    recorder.close()

# getFileList: get file list of path #
def configReader(section='', option=''):
    conf = ConfigParser.ConfigParser()
    conf.read('config.cfg')
    if section!='':
        return conf.get(section, option) if option!='' else conf.items(section)
    return [conf.items(section) for section in conf.sections]

# RaiseErr: raise error and save #
def RaiseErr(key, msg):
    global ErrorMsg
    ErrorMsg[key].append(msg+'\n')
    printInfo("Error "+key+":\n"+str([msg if msg!=None else '']))

# OutputErr: output error counts #
def OutputErr():
    global ErrorMsg
    pos_erro = configReader(section='path',option='pos_erro')
    for key in ErrorMsg.iterkeys():
        if len(ErrorMsg[key]):
            print "Error %s Counts: %d"%(key, len(ErrorMsg[key]))
            dataWriter(ErrorMsg[key], pos_erro%key)

# lookup: Get a method or class from any imported module from its name.
def lookup(name, namespace):
    dots = name.count('.')
    if dots > 0:
        moduleName, objName = '.'.join(name.split('.')[:-1]), name.split('.')[-1]
        module = __import__(moduleName)
        return getattr(module, objName)
    else:
        modules = [obj for obj in namespace.values() if str(type(obj)) == "<type 'module'>"]
        options = [getattr(module, name) for module in modules if name in dir(module)]
        options += [obj[1] for obj in namespace.items() if obj[0] == name ]
        if len(options) == 1: return options[0]
        if len(options) > 1: raise Exception, 'Name conflict for %s'%options[0]
        raise Exception, '%s not found as a method or class' % name

# http2str: get string from http link
rep = dict((re.escape(k), v) for k, v in {'/':'_', ':':'_', '.':'_'}.iteritems())
pattern = re.compile("|".join(rep.keys()))
def http2str(http):
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], http)