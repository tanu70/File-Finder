import PySimpleGUI as gui
from threading import Thread

'''gui.theme('TanBlue')
dirInput = gui.Input(key='dirUrls', enable_events= True, readonly =True)
browseButton = gui.FolderBrowse(enable_events= True)

fileName = gui.Input(key="filePhrase")
searchButton = gui.Button('Search')

a = gui.Slider(range=(1,5),default_value= 2, orientation= 'h', border_width=1)
b = gui.Multiline("No File",size= (50,5), disabled= True , text_color= gui.rgb(50,50,50))

dirBrowseTitle = gui.Text('Choose a Directory:')

fileSearchTitle = gui.Text('Enter File Name:')

progress = gui.Progress(max_value = 10, size = (30,15), orientation = 'h', key='progressBar')

resultText = gui.Text('Search Results:')

layout = [[a], [dirBrowseTitle], [dirInput, browseButton], [fileSearchTitle], [fileName,searchButton], [resultText], [b]]
window = gui.Window('File Search', layout, resizable= True)


while True:
    prevChosenDir = None
    tmpDic = {}
    with open('chosenDir.json','r') as ir:
        
        try:
            tmpDic = json.load(ir)
            prevChosenDir = tmpDic['dir']
        except:
            tmpDic = {}
    
    if prevChosenDir is not None:
        print(prevChosenDir)
        dirInput.DefaultText = prevChosenDir
        browseButton.InitialFolder = prevChosenDir
    print('--Tanu---')
    event, values = window.read()
    i=1
    while i <10000:
        a.update(i%6)
        i+=1
    print('--------Tanu--------')
    i = 0
    # layout.append(b)
    # b.update(visib)
    print("Event  ---  ",event , " ----- ", values)

    if event == gui.WIN_CLOSED :
        a = 9
        break
    else :
        try:
            dirrr = values['dirUrls']
            tmpDic['dir']=dirrr
            tmpJson = json.dumps(tmpDic)
            print(tmpJson)
            with open('chosenDir.json','w') as ir:
                print("Writing  ", tmpJson)
                ir.write(tmpJson)
            phrase = values['filePhrase']
            files = os.listdir(dirrr)
            print("Files  ", files)
            b.update('',text_color=gui.rgb(0,0,0))
            for fileUrl in files:
                if fileUrl.__contains__(phrase):
                    print(" --Got-- ",fileUrl)
                    b.write(fileUrl+'\n')
                else:
                    print(" --Didn't Got-- ",fileUrl)
        except:
            print("   --FAILED--   ")'''
        


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
    __matchedFilesField = gui.Multiline("No File",key = 'matchedFilesFie',size= (50,5), disabled= True , text_color= gui.rgb(50,50,50), horizontal_scroll= True)
    __progressBar = gui.ProgressBar(max_value= 100)
    __progressBarTitle = gui.Text()

    __dirSelectionColumn = None
    __searchColumn = None
    __resultColumn = None
    __progressColumn = None

    layout = []
    displayWindow = gui.Window(title= 'Search File',resizable= True)


    def __init__(self):
        pass


    """def initiateSavedData(self):
        tmpDic = {}
        with open('chosenDir.json','r') as ir:
            try:
                tmpDic = json.load(ir)
                self.chosenDir = tmpDic['dir']
            except:
                tmpDic = {}"""

    
    def __initiateGUIWindow(self, setDir = None):
        chosenDir = setDir
        if chosenDir is not None:
            self.__dirUrlField.DefaultText = chosenDir
            self.__dirBrowseButton.InitialFolder = chosenDir
        
        # self.layout = [[self.dirUrlField, self.dirBrowseButton], [self.fileNameField, self.fileSearchButton]]

        self.__dirSelectionColumn = gui.Column(layout= [[self.__dirSelectionTitle], [self.__dirUrlField, self.__dirBrowseButton]], key = 'dirSelectionColumn')
        self.__searchColumn = gui.Column(layout = [[self.__searchFieldTitle], [self.__fileNameField, self.__fileSearchButton]], key = 'searchColumn')
        self.__resultColumn = gui.Column(layout= [[self.__matchedFilesField]], key = 'resultColumn', visible= False)
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
                print("--- dirUrlField ---", values)
                self.__updateChosenDirectory(values)
            elif event == 'Search':
                print('--- Search ---', values)
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

    
    def updateGuiWithResult(self, fileList):
        
        print('Came To Update')
        resultFiles = fileList
        resultFiles = '\n'.join(resultFiles)
        if resultFiles == '':
            resultFiles = 'No Files'
        else:
            resultFiles += '\n'
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

    def enableInteraction(self):
        self.__dirBrowseButton.update(disabled= False)
        self.__fileSearchButton.update(disabled= False)
        return
    

    def updateSelectedDirInBrowsing(self, updatedDir):
        self.__dirBrowseButton.InitialFolder = updatedDir

    '''def updateSavedData(self):
        tempDic = {}
        tempDic['dir'] = self.chosenDir
        print('Check Check   ', tempDic, type(tempDic))
        tempJson = json.dumps(tempDic)
        with open('chosenDir.json','w') as ir:
            ir.write(tempJson)
        print(tempDic)
        return'''
