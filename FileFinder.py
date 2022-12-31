from DataModel import DataModel
from FileSearchGUI import FileSearchGUI
import time
from threading import Thread


class FileFinder:

    __guiWindow = None
    __dataModel = None
    __isSearchingInProgress:bool = False
    __isIndexingInProgress:bool = False
    __searchingPhrase: str = ''
    __pendingSearch = False

    __totalMatchedFiles:int = 0

    def __init__(self) -> None:
        self.__guiWindow = FileSearchGUI()
        self.__initiateGUI()

        self.__dataModel = DataModel()
        self.__initiateDataModel()
        return


    def __initiateGUI(self):
        self.__guiWindow.searchFilesCallback = self.searchInFiles
        self.__guiWindow.getCurrentDirCallback = self.getCurrentDirectory
        self.__guiWindow.directoryUpdateCallback = self.directoryUpdate
        return


    def __initiateDataModel(self):
        self.__dataModel.updateGuiWithResultCallback = self.updateResultsInGUI
        self.__dataModel.directoryUpdateCompletionCallback = self.indexingCompletionUpdate
        self.__dataModel.fileSearchingCompletionCallback = self.searchingCompletionUpdate
        self.__dataModel.progressValueUpdateCallback = self.updateProgressValue
        self.__dataModel.savedIndexingRetriveFailedCallback = self.savedIndexingRetriveFailed
        self.__dataModel.indexingRetriveCompletionCallback = self.savedIndexingRetrivingCompleted
        self.__dataModel.needToUpdateFileListCallback = self.filesNeedToUpdate
        self.__dataModel.searchingCancelCallback = self.searchWithNewPhrase
        return


    def startApp(self):
        self.__guiWindow.displaySearchingGUI(setDir= self.getCurrentDirectory())
        time.sleep(0.5)
        if self.__dataModel.getSelectedDir() is None:
            self.__guiWindow.disableSearchButton()
        else:
            self.retriveSavedIndexing()
        
        # self.filesNeedToUpdate()
        return


    def retriveSavedIndexing(self):
        self.__guiWindow.disableInteraction()
        self.clearOutputField()
        self.__guiWindow.showProgressBar(title= 'Indexing Files...')
        self.__dataModel.retriveSavedFileIndexing()
        return


    def directoryUpdate(self, dirUrl = None):
        self.__isIndexingInProgress = True
        self.__guiWindow.disableInteraction()
        self.clearOutputField()
        self.__guiWindow.showProgressBar(title =  'Indexing Files...')
        self.__dataModel.updateChosenDir(dirUrl= dirUrl)
        self.__guiWindow.updateSelectedDirInBrowsing(updatedDir = dirUrl)
        return


    def searchInFiles(self, phrase = None):
        self.__searchingPhrase = phrase

        if self.__isSearchingInProgress is True:
            self.__pendingSearch = True
            self.__dataModel.shouldStopSearching = True
            while self.__pendingSearch:
                time.sleep(0.5)
        
        if self.__dataModel.checkIndexingValidity() is False:
            self.filesNeedToUpdate()
            
        self.__isSearchingInProgress = True
        self.clearOutputField()
        self.__guiWindow.showProgressBar(title= 'Searching Files...')
        searchThread = Thread(target = self.__dataModel.searchInFiles,args= (phrase,))
        searchThread.start()
        return


    def getCurrentDirectory(self):
        currentDir = self.__dataModel.getSelectedDir()
        return currentDir


    def updateResultsInGUI(self, matchedFiles):
        self.__totalMatchedFiles += len(matchedFiles)
        self.__guiWindow.updateGuiWithResult(matchedFiles, totalFiles= self.__totalMatchedFiles)
        return


    def clearOutputField(self):
        self.__guiWindow.ClearOutputField()
        self.__totalMatchedFiles = 0
        return


    def updateProgressValue(self, value):
        self.__guiWindow.updateProgressBarValue(value = value)
        return


    def searchingCompletionUpdate(self):
        self.__isSearchingInProgress = False
        self.__guiWindow.updateGuiWithResult([],totalFiles= self.__totalMatchedFiles)
        self.__guiWindow.closeProgress()
        return


    def indexingCompletionUpdate(self):
        self.__isIndexingInProgress = False
        self.__guiWindow.closeProgress()
        self.__guiWindow.enableInteraction()
        if self.__dataModel.getSelectedDir() is None:
            self.__guiWindow.disableSearchButton()
        return

    
    def processCanceledFromDataMode(self):
        self.__guiWindow.closeProgress()
        self.searchInFiles(phrase= self.__searchingPhrase)
        return

    
    def savedIndexingRetriveFailed(self):
        self.__guiWindow.closeProgress()
        self.__guiWindow.enableInteraction()
        if self.getCurrentDirectory() is not None:
            self.directoryUpdate()
        return
    

    def savedIndexingRetrivingCompleted(self):
        self.__guiWindow.enableInteraction()
        self.__guiWindow.closeProgress()
        return

    
    def filesNeedToUpdate(self):
        try:
            self.directoryUpdate(dirUrl= self.getCurrentDirectory())
        except KeyError:
            print('--- FAILED to Update File List ---', KeyError)
        return
    

    def searchWithNewPhrase(self):
        self.__dataModel.shouldStopSearching = False
        self.__pendingSearch = False
        return




def main() -> None:
    fileFinderGUI = FileFinder()
    fileFinderGUI.startApp()



if __name__ == '__main__':
    main()