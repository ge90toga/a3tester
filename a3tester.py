import ctypes
import sys
import subprocess
from os.path import isfile, join, abspath
from os import listdir

SHOW_FREQ = False
stemNativeCLib = ctypes.CDLL('./stemlib/stmr.so')
'''
should be under of ./yourassignment/a3tester
'''

class FileFreqPair:
    def __init__(self, fileName, fileFreq):
        self.fileName = fileName
        self.fileFreq = fileFreq

    def __lt__(self, other):
        if self.fileFreq > other.fileFreq:
            return True
        if self.fileFreq < other.fileFreq:
            return False
        if self.fileFreq == other.fileFreq:
            return self.fileName < other.fileName

class A3Test:

    def __init__(self):
        self.PARENT_DIR = str(abspath('..'))
        self.TEST_FILE_DIR = self.PARENT_DIR + '/' + sys.argv[1]
        self.INDEX_DIR = self.PARENT_DIR + '/' + sys.argv[2]
        self.ORIGIN_TERM_LIST = sys.argv[3:len(sys.argv)]
        self.TERM_LIST = sys.argv[3:len(sys.argv)]
        self.TERM_LIST = list(map(lambda x: x.lower(), self.TERM_LIST))

    def go(self):
        self.stemTermList()
        self.wordFileFreqDic = {}
        self.wordMatchSet = {}  # key term value: the set which contains all file name that matches it
        self.readAllFiles()
        self.dicFinalCount = {}
        self.intersectedFileSet = self.intersectFileNameSet()
        self.computeFreq()
        self.produceFinalRankingTable()
        self.runUserA3Search()
        self.compareTwoResult()

    def stemAWord(self, word):
        inputArg = ctypes.c_char_p(bytes(word, encoding='ascii'))
        stemNativeCLib.callStemNative(inputArg)
        return inputArg.value.decode(encoding='ascii')

    def stemTermList(self):
        stemedList = []
        for term in self.TERM_LIST:
            stemedWord = self.stemAWord(term)
            stemedList.append(stemedWord)
        # create a dictionary recording each term's freq in a certain file
        self.TERM_LIST = stemedList

    def readAllFiles(self):
        print("RUNNING TEST SCRIPT'S SEARCH, COULD BE A BIT SLOW...")
        textFiles = [f for f in listdir(self.TEST_FILE_DIR) if isfile(join(self.TEST_FILE_DIR, f))]
        for fileName in textFiles:
            filePath = join(self.TEST_FILE_DIR, fileName)
            self.searchFile(filePath, fileName)

    def searchFile(self, filePath, fileName):
        # print("searching file {0}".format(fileName))
        with open(filePath, 'rb') as file:
            for line in file:
                word = ""
                for c in line:
                    if (c >= 65 and c <= 90) or (c >= 97 and c < 122):
                        word += chr(c)
                    else:
                        if len(word) >= 3:
                            pass
                            self.updateMatchingTableSingle(word, fileName)
                        word = ""

    def updateMatchingTable(self, matches, fileName):
        for word in matches:
            sWord = self.stemAWord(word.lower())
            # stdout.write("\r%s" % sWord)
            # stdout.flush()
            if sWord in self.TERM_LIST:
                self.updateWordFileInDic(sWord, fileName)
                self.updateTermMatchSet(sWord, fileName)

    def updateMatchingTableSingle(self, word, fileName):
        sWord = self.stemAWord(word.lower())
        if sWord in self.TERM_LIST:
            self.updateWordFileInDic(sWord, fileName)
            self.updateTermMatchSet(sWord, fileName)

    def updateWordFileInDic(self, word, fileName):
        if word in self.wordFileFreqDic:
            if fileName in self.wordFileFreqDic[word]:
                self.wordFileFreqDic[word][fileName] += 1
            else:
                self.wordFileFreqDic[word][fileName] = 1
        else:
            self.wordFileFreqDic[word] = {fileName: 1}

    def updateTermMatchSet(self, word, fileName):
        if word in self.wordMatchSet:
            self.wordMatchSet[word].add(fileName)
        else:
            fileNameSet = set()
            fileNameSet.add(fileName)
            self.wordMatchSet[word] = fileNameSet

    def intersectFileNameSet(self):
        if len(self.TERM_LIST) != len(self.wordMatchSet):
            return None
        # intersect sets
        # for i in range(1,len(self.TERM_LIST)):
        if len(self.TERM_LIST) > 1:
            merged = self.wordMatchSet[self.TERM_LIST[0]].intersection(self.wordMatchSet[self.TERM_LIST[1]])
            if len(merged) == 0:
                return None
            for i in range(2, len(self.TERM_LIST)):
                merged = self.wordMatchSet[self.TERM_LIST[i]].intersection(merged)
                if len(merged) == 0:
                    return None
            return merged
        else:
            return self.wordMatchSet[self.TERM_LIST[0]]

    def computeFreq(self):
        if self.intersectedFileSet != None:
            for term in self.TERM_LIST:
                for file in self.intersectedFileSet:
                    freq = self.wordFileFreqDic[term][file]
                    if file in self.dicFinalCount:
                        self.dicFinalCount[file] += freq
                    else:
                        self.dicFinalCount[file] = freq

    def produceFinalRankingTable(self):
        rankingTable = []
        for key in self.dicFinalCount:
            rankingTable.append(FileFreqPair(key, self.dicFinalCount[key]))
        rankingTable.sort()
        self.writeScriptToFile(rankingTable)

    def writeScriptToFile(self, rankingTable):
        with open('script.out.txt', 'w') as file:
            if len(rankingTable) == 0:
                file.write("\n")
            else:
                for pair in rankingTable:
                    if SHOW_FREQ:
                        file.write("{0} {1}\n".format(pair.fileName, pair.fileFreq))
                    else:
                        file.write("{0}\n".format(pair.fileName))

    def writeA3ResultToFile(self, result):
        with open('cpp.out.txt', 'w') as file:
            file.write(result)

    def runUserA3Search(self):
        print("RUNNING USER C/C++ a3search...")
        cmd = []
        promgram = self.PARENT_DIR + '/' + 'a3search'
        textFolder = self.TEST_FILE_DIR
        indexFolder = self.INDEX_DIR
        cmd.append(promgram)
        cmd.append(textFolder)
        cmd.append(indexFolder)
        for term in self.ORIGIN_TERM_LIST:
            cmd.append(term)
        ouput = subprocess.check_output(cmd, stderr=subprocess.PIPE)
        self.writeA3ResultToFile(ouput.decode())

    def compareTwoResult(self):
        print("COMPARING SCRIPT VS C/C++")
        cppReuslt = []
        pyResult = []
        with open('cpp.out.txt', 'r') as cppResultFile:
            cppReuslt = cppResultFile.read().split(sep='\n')
        with open('script.out.txt') as scriptResultFile:
            pyResult = scriptResultFile.read().split(sep='\n')
        if len(cppReuslt) != len(pyResult):
            print("THE RESULT COUNT IS NOT THE SAME C/C++ GOT: {0} SCRIPT GOT: {1}".format(len(cppReuslt),len(pyResult)))
            return
        for lineNum in range(len(cppReuslt)):
            if cppReuslt[lineNum] != pyResult[lineNum]:
                print("MISMATCH AT LINE: "
                      "{0} C/C++ GOT: {1} SCRIPT GOT: {2}".format(lineNum + 1, cppReuslt[lineNum], pyResult[lineNum]))
                return

        print("TEST PASSED")


a3 = A3Test()
# print(a3.stemAWord("protect"))
a3.go()