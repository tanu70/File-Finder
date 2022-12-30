import json
import os
import time
from threading import Thread

class DataModel:

    __fileNameList: list[str] = []
    __matchedFileIndex: list[int] = []
    __chosenDir = None
    __indexingSaveFileName = 'fileIndexing.json'
    __currentDirectoryLastUpdateTime = 0.0

    __mapingFiles = {}
    __searchingPhrase: str = ''
    __LCPArray: list[int] = []
    __filteredFileList = []

    directoryUpdateCompletionCallback = None
    fileSearchingCompletionCallback = None
    progressValueUpdateCallback = None
    savedIndexingRetriveFailedCallback = None
    updateGuiWithResultCallback = None
    indexingRetriveCompletionCallback = None
    needToUpdateFileListCallback = None

    shouldStopSearching:bool = False
    searchingCancelCallback = None

    __shouldStopFakeProgress: bool = False

    def __init__(self) -> None:
        self.initiateSelectedDir()
        return


    def getSelectedDir(self):
        return self.__chosenDir
    

    def initiateSelectedDir(self):
        tmpDic = {}
        with open('chosenDir.json','r') as ir:
            try:
                tmpDic = json.load(ir)
                self.__chosenDir = tmpDic['dir']
            except:
                self.__chosenDir = None    


    def updateChosenDir(self, dirUrl = None):
        print('--- Came To Update Chosen Dir ---')
        if dirUrl == None:
            tmpDic = {}
            with open('chosenDir.json','r') as ir:
                try:
                    tmpDic = json.load(ir)
                    dirUrl = tmpDic['dir']
                except:
                    pass 
        else:
            with open('chosenDir.json','w') as ir:
                tmpDic = {'dir': dirUrl}
                tmpJson = json.dumps(tmpDic)
                ir.write(tmpJson)

        if dirUrl == None:
            return
        self.__chosenDir = dirUrl

        try:
            self.progressValueUpdateCallback(value = 10)
        except:
            print('--- Error!! Initial Progress Failed in Directory Update ---')

        self.updateFileList()
        self.__saveFileIndexing()
        try:
            self.directoryUpdateCompletionCallback()
        except:
            print('---- ERROR!!! Directory Update Completion Callback Error ----')

        return


    def updateFileList(self, fileList = None) -> None:
        if fileList == None:
            self.__fileNameList = os.listdir(self.__chosenDir)
        else:
            self.__fileNameList = fileList
        
        try:
            self.progressValueUpdateCallback(value = 20)
        except:
            print('--- ERROR!!! Progress Value Update Failed After listing New Files ---')
            
        try:
            self.__currentDirectoryLastUpdateTime = self.__getLastUpdateTime(forDirectory= self.__chosenDir)
        except KeyError:
            print('-- ERROR Geting last Updated Time --', KeyError)

        print('--- totalFiles ----', len(self.__fileNameList))
        self.__fileInedxing()
        return


    def searchInFiles(self, phrase) -> None:
        self.__matchedFileIndex = []
        self.__searchingPhrase = phrase
        self.__buildLcpArray()

        lastUpdatedResultInd:int = -1

        if self.shouldStopSearching:
            self.searchingCancelCallback()
            return

        self.__filterFiles()
        if self.shouldStopSearching:
            self.searchingCancelCallback()
            return

        totalFileToMatch = len(self.__filteredFileList)
        multiplyFactor = 70.0/ max(1,totalFileToMatch)
        progressUpdateIndx = int(totalFileToMatch/15)
        progressUpdateIndx = max(1,progressUpdateIndx)

        resultUpdateIndx = int(totalFileToMatch/15)
        resultUpdateIndx = max(1,resultUpdateIndx)

        for i in range(0,len(self.__filteredFileList),1):
            
            idx =  self.__filteredFileList[i]
            if self.__matchFileAndPhrase(idx) is True:
                self.__matchedFileIndex.append(idx)

            if self.shouldStopSearching:
                self.searchingCancelCallback()
                return
            
            if i%progressUpdateIndx == 0:
                try:
                    self.progressValueUpdateCallback(value = 30 + ((i+1)*multiplyFactor))
                except:
                    print('--- FAILED!!! Progress Update Failed in File Matching ---')
            
            if i%resultUpdateIndx == 0:
                try:
                    lastUpdatedResultInd = self.__sendMatchedFileList(fromInd=lastUpdatedResultInd + 1)
                except KeyError:
                    print('--- Failed to Send Matched File Update ---', KeyError)

        print('- lastUpdated -', lastUpdatedResultInd)
        try:
            lastUpdatedResultInd = self.__sendMatchedFileList(fromInd= lastUpdatedResultInd + 1)
            self.fileSearchingCompletionCallback()
        except:
            print('---- ERROR!!!! File Searching Completion Callback Failed ----')
        return


    def __sendMatchedFileList(self, fromInd:int = 0) -> int:
        retList: list[str] = []
        
        for idx in range(fromInd, len(self.__matchedFileIndex), 1):
            retList.append(self.__fileNameList[self.__matchedFileIndex[idx]])
        
        print('check check -', fromInd, len(self.__matchedFileIndex), retList)
        if len(retList) == 0:
            return fromInd - 1

        try:
            self.updateGuiWithResultCallback(retList)
        except:
            print('--- FAILED!!! Couldn\'t send matched list ---')
        
        return len(self.__matchedFileIndex) - 1


    def __fileInedxing(self):

        self.__mapingFiles = {}
        totalFiles = len(self.__fileNameList)
        multiplyFactor = 70.0 / max(1,totalFiles)
        updateIndx = int(totalFiles/14)
        updateIndx = max(updateIndx, 1)

        for i in range(0,len(self.__fileNameList),1):
            for j in range(0,len(self.__fileNameList[i])-2,1):
                tmpString = self.__fileNameList[i][j:j+3]
                # if self.__mapingFiles[tmpString] == None:
                    # self.__mapingFiles[tmpString] = []
                try:
                    self.__mapingFiles[tmpString].append(i)
                except:
                    self.__mapingFiles[tmpString] = [i]
            
            if i%updateIndx == 0:
                try:
                    self.progressValueUpdateCallback(value = 20+((i+1)*multiplyFactor))
                except:
                    print('--- ERROR!!! Progress Value Update Failed in Indexing ---')
            
        return


    def __buildLcpArray(self):
        if self.__searchingPhrase is not None:
            self.__LCPArray = [0]
            for i in range(1,len(self.__searchingPhrase),1):
                j = self.__LCPArray[i-1]

                if self.shouldStopSearching:
                    return

                while j>0:
                    if self.__searchingPhrase[j]==self.__searchingPhrase[i]:
                        break
                    j = self.__LCPArray[j]
                self.__LCPArray.append(j)
        return  


    def __matchFileAndPhrase(self, fileInd) -> bool:
        fileName = self.__fileNameList[fileInd]
        nextMatch = 0
        fileSize = len(fileName)
        matchSize = len(self.__searchingPhrase)
        for i in range(0,fileSize,1):

            if self.shouldStopSearching:
                return

            if nextMatch >= matchSize:
                break

            while nextMatch > 0:
                if fileName[i] == self.__searchingPhrase[nextMatch]:
                    break
                nextMatch = self.__LCPArray[nextMatch]

            if self.__searchingPhrase[nextMatch] == fileName[i]:
                nextMatch += 1

        return nextMatch >= matchSize


    def __filterFiles(self):
        print('--- Came to Filtering ---')
        matchCount = {}
        self.__filteredFileList = []
        
        searchLen = len(self.__searchingPhrase)
        multiplyFactor = 30.0/max(1,(searchLen - 2))
        updateIndx = int(searchLen/7)
        updateIndx = max(updateIndx,1)

        for i in range(0,len(self.__searchingPhrase)-2,1):

            if self.shouldStopSearching:
                return
            
            tmpPhrase = self.__searchingPhrase[i:i+3]
            indices = []
            try:
                indices = self.__mapingFiles[tmpPhrase]
            except:
                pass

            for ind in indices:
                try:
                    matchCount[ind] += 1
                except:
                    matchCount[ind]=1
            
            if i%updateIndx == 0:
                try:
                    self.progressValueUpdateCallback(value = (i+1)*multiplyFactor)
                except:
                    print('--- ERROR!!! Update Progress Failed in File Filtering ---')

        
        matchSize = len(self.__searchingPhrase)
        for i in range (0,len(self.__fileNameList),1):
            if self.shouldStopSearching:
                return
            cnt = 0
            try:
                cnt = matchCount[i]
            except:
                pass
            if matchSize < 3 or cnt == matchSize-2:
                self.__filteredFileList.append(i)
        print('---- Filtered Result ----', len(self.__filteredFileList))
        return

    
    def __saveFileIndexing(self):
        mappingJson = json.dumps({
            'mappedFiles': self.__mapingFiles,
            'fileNames': self.__fileNameList,
            'directoryLastUpdateTime': self.__currentDirectoryLastUpdateTime
        })

        with open(self.__indexingSaveFileName,'w') as fjson:
            try:
                fjson.write(mappingJson)
            except:
                print('--- ERROR!!! Indexing Saving Failed ---')
            fjson.close()
        self.progressValueUpdateCallback(value = 100)
        return
    

    def retriveSavedFileIndexing(self):
        print('Came to retrive')
        self.__createFakeProgress(5)
        with open(self.__indexingSaveFileName,'r') as fjson:
            try:
                tmpDic = json.load(fjson)
                self.__fileNameList = tmpDic['fileNames']
                self.__mapingFiles = tmpDic['mappedFiles']
                self.__currentDirectoryLastUpdateTime = tmpDic['directoryLastUpdateTime']
                self.__shouldStopFakeProgress = True
                self.indexingRetriveCompletionCallback()

                if self.checkIndexingValidity() == False:
                    try:
                        self.needToUpdateFileListCallback()
                    except KeyError:
                        print('---- Failed to Send File List Update Callback ----', KeyError)
                
                '''self.progressValueUpdateCallback(100)
                try:
                    self.indexingRetriveCompletionCallback()
                except:
                    print('--- FAILED to Send Completion for Indexing Retriving ---')'''
            except:
                print('--- ERROR!!! Failed to Retrive Saved Indexing ---')
                self.savedIndexingRetriveFailedCallback()


    def __createFakeProgress(self, targetTime = 5):
        progressThread = Thread(target= self.__FakeProgress, args= (targetTime,))
        progressThread.start()
        

    def __FakeProgress(self, targetTime = 5):
        progressUnit = 95/targetTime
        print('--- came to fake progress ---')
        for i in range(0,targetTime,1):
            time.sleep(1)
            if self.__shouldStopFakeProgress:
                return
            try:
                self.progressValueUpdateCallback((i+1)*progressUnit)
            except:
                print('-- Auto progress UpdateFailed --')
        return


    def checkIndexingValidity(self) -> bool:
        if self.__chosenDir is None:
            return False
        
        lastUpdated = self.__getLastUpdateTime(forDirectory= self.__chosenDir)
        if lastUpdated > self.__currentDirectoryLastUpdateTime:
            return False
        return True


    def __getLastUpdateTime(self, forDirectory):
        updateTime = os.path.getmtime(forDirectory)

        print('--Time--', updateTime)
        return updateTime
