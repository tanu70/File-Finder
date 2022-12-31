import PySimpleGUI as gui
from threading import Thread



class FileSearchGUI:

    directoryUpdateCallback = None
    searchFilesCallback = None
    getCurrentDirCallback = None

    __dirSelectionTitle = gui.Text('Choose a directory:')
    __dirUrlField = gui.Input(key = 'dirUrlField', readonly= True, enable_events= True)
    __dirBrowseButton = gui.FolderBrowse(enable_events= True)
    __searchFieldTitle = gui.Text('Enter file name:')
    __fileNameField = gui.Input(key= 'fileNameField', enable_events = False)
    __fileSearchButton = gui.Button('Search')
    __resultFieldTitle = gui.Text('',key= 'resultFieldTitle')
    __matchedFilesField = gui.Multiline("No File",key = 'matchedFilesFie',size= (100,20), disabled= True , text_color= gui.rgb(50,50,50), horizontal_scroll= True)
    __progressBar = gui.ProgressBar(max_value= 100, size = (50,2))
    __progressBarTitle = gui.Text()

    __dirSelectionColumn = None
    __searchColumn = None
    __resultColumn = None
    __progressColumn = None

    layout = []
    displayWindow = gui.Window(title= 'Search File',resizable= True)


    def __init__(self):
        pass


    def __initiateGUIWindow(self, setDir = None):
        chosenDir = setDir
        if chosenDir is not None:
            self.__dirUrlField.DefaultText = chosenDir
            self.__dirBrowseButton.InitialFolder = chosenDir
        
        # self.layout = [[self.dirUrlField, self.dirBrowseButton], [self.fileNameField, self.fileSearchButton]]

        self.__dirSelectionColumn = gui.Column(layout= [[self.__dirSelectionTitle], [self.__dirUrlField, self.__dirBrowseButton]], key = 'dirSelectionColumn')
        self.__searchColumn = gui.Column(layout = [[self.__searchFieldTitle], [self.__fileNameField, self.__fileSearchButton]], key = 'searchColumn')
        self.__resultColumn = gui.Column(layout= [[self.__resultFieldTitle], [self.__matchedFilesField]], key = 'resultColumn', visible= False)
        self.__progressColumn = gui.Column(layout= [[self.__progressBarTitle],[self.__progressBar]], visible= False)
        
        self.layout = [[self.__dirSelectionColumn],[self.__searchColumn], [self.__resultColumn], [self.__progressColumn]]
        self.displayWindow.layout(self.layout)
        
        return


    def __continueDisplayingGUI(self):
        print(" Displayed ")
        while True:
            event, values = self.displayWindow.read()

            if event == gui.WINDOW_CLOSED:
                break
            elif event == 'dirUrlField':
                # print("--- dirUrlField ---", values)
                self.__updateChosenDirectory(values)
            elif event == 'Search':
                # print('--- Search ---', values)
                self.__searchFiles(withPhrase= values['fileNameField'])


    def displaySearchingGUI(self, setDir = None):
        self.__initiateGUIWindow(setDir= setDir)
        displayThread = Thread(target= self.__continueDisplayingGUI)
        displayThread.start()
        return
    

    def __searchFiles(self, withPhrase= None):
        if withPhrase is not None:
            print('---Searching---', withPhrase)
            self.searchFilesCallback(phrase= withPhrase)
            
            # self.updateGuiWithResult()

    
    def ClearOutputField(self):
        self.__matchedFilesField.update("")
        return


    def updateGuiWithResult(self, fileList, totalFiles:int = 0):
        
        resultFiles = fileList
        resultFiles = '\n'.join(resultFiles)
        if totalFiles == 0:
            resultFiles = 'No Files\n'
        elif len(fileList) > 0:
            resultFiles += '\n'
        
        self.__resultFieldTitle.update(f'Matched Files: {totalFiles}')
        self.__matchedFilesField.update(resultFiles, append= True)
        self.__resultColumn.update(visible= True)
        return


    def __updateChosenDirectory(self, values):
        self.directoryUpdateCallback(dirUrl= values['dirUrlField'])
        self.__resultColumn.update(visible= False)
        return


    def showProgressBar(self, title = ''):
        self.__progressBarTitle.update(value= title)
        self.__progressBar.update(current_count= 3)
        self.__progressColumn.update(visible= True)
        return


    def updateProgressBarValue(self, value):
        self.__progressBar.update(current_count= value)
        return


    def closeProgress(self):
        self.__progressColumn.update(visible= False)
        return


    def disableInteraction(self):
        self.__dirBrowseButton.update(disabled= True)
        self.__fileSearchButton.update(disabled= True)
        return


    def disableSearchButton(self):
        self.__fileSearchButton.update(disabled = True)

    def enableInteraction(self):
        self.__dirBrowseButton.update(disabled= False)
        self.__fileSearchButton.update(disabled= False)
        return
    

    def updateSelectedDirInBrowsing(self, updatedDir):
        self.__dirBrowseButton.InitialFolder = updatedDir
        return