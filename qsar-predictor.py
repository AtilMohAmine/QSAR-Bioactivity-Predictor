import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QDialog, QTableView, QPushButton, QFileDialog, QMessageBox, QWidget, QMenuBar, QMenu, QAction, QLabel
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pickle
import os
import pandas as pd
from windows import SelectionWindow, ProgressWindow, PredictWindow, AboutWindow
from utils import PandasModel

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('QSAR Bioactivity Predictor')
        self.setGeometry(200, 200, 800, 500)
        self.targetName = None

        # Create the menu bar
        self._createActions()
        self._createMenuBar()


    def initUI(self):
        self.targetNameLabel = QLabel()
        self.scoreLabel = QLabel()
        self.features = QLabel()
        tableLabel = QLabel('Used activities:')
        self.table_view = QTableView()
        self.loadCSVButton = QPushButton('Load your CSV data', self)
        self.loadCSVButton.clicked.connect(self.loadCSV)

        LeftLayout = QVBoxLayout()
        LeftLayout.addWidget(self.scoreLabel)
        LeftLayout.addWidget(self.features)
        LeftLayout.addWidget(tableLabel)
        LeftLayout.addWidget(self.table_view)
        LeftLayout.addWidget(self.loadCSVButton)

        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)

        Hlayout = QHBoxLayout()
        Hlayout.addLayout(LeftLayout, 1)
        Hlayout.addWidget(self.canvas)

        layout = QVBoxLayout()
        layout.addWidget(self.targetNameLabel)
        layout.addLayout(Hlayout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def showPlot(self):
        # create the Seaborn plot
        sns.set(color_codes=True)
        sns.set_style("white")

        ax = sns.regplot(x=self.modelData['Y_test'], y=self.modelData['Y_pred'], scatter_kws={'alpha':0.4})
        ax.set_xlabel('Experimental pIC50', fontsize='large', fontweight='bold')
        ax.set_ylabel('Predicted pIC50', fontsize='large', fontweight='bold')
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 12)
        #ax.figure.set_size_inches(5, 5)

        self.figure = plt.figure(figsize=(5, 5))
        self.canvas.draw()

    def _createMenuBar(self):
        menuBar = QMenuBar(self)
        # File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)
        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)
        # Help menu
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)
        
        self.setMenuBar(menuBar)

    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        self.newAction.triggered.connect(self.newModel)
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.openAction.triggered.connect(self.openModel)
        self.saveAction = QAction("&Save", self)
        self.saveAction.triggered.connect(self.saveModel)
        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(self.exit_app)

        self.copyAction = QAction("&Copy", self)
        self.copyAction.setShortcut('Ctrl+C')
        self.copyAction.setStatusTip('Copy to the Clipboard')
        #self.copyAction.triggered.connect(QtGui.QTextEdit.copy(self))


        self.pasteAction = QAction("&Paste", self)
        self.pasteAction.setShortcut('Ctrl+V')
        self.pasteAction.setStatusTip('Paste from the Clipboard')
        #self.pasteAction.triggered.connect(QtGui.QTextEdit.paste(self))

        self.cutAction = QAction("C&ut", self)
        self.cutAction.setShortcut('Ctrl+X')
        self.cutAction.setStatusTip('Copy text to the clipboard and delet from editor')
        #self.cutAction.triggered.connect(QtGui.QTextEdit.cut(self))

        self.helpContentAction = QAction("&Help Content", self)
        self.helpContentAction.triggered.connect(self.open_repo)

        self.aboutAction = QAction("&About", self)
        self.aboutAction.triggered.connect(self.show_about_dialog)

    def newModel(self):
        self.SelectionWindow = SelectionWindow()
        self.SelectionWindow.targetSignal.connect(self.handleTargetSignal)
        self.SelectionWindow.setGeometry(100, 100, 800, 400)
        self.SelectionWindow.show()

    def handleTargetSignal(self, target):
        self.ProgressWindow = ProgressWindow(target['chemblId'])
        self.chemblId = target['chemblId']
        self.targetName = target['targetName']
        self.ProgressWindow.modelReady.connect(self.loadModel)
        self.ProgressWindow.show()

    def loadModel(self, data):
        self.initUI()
        self.modelData = data
        self.targetNameLabel.setText('Bioactivity Prediction for {target}'.format(target = self.targetName))
        self.scoreLabel.setText('Model score: {score:.2f}'.format(score=self.modelData['score']))
        self.features.setText('Features: {features}'.format(features=len(self.modelData['selected_cols'])))
        self.table_view.setModel(PandasModel(self.modelData['df']))
        self.showPlot()

    def saveModel(self):
        if self.targetName == None:
            QMessageBox.warning(self, 'Save model', 'Create model first') 
            return
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Pickle (*.pkl)')
        if file_path: 
            file_path = os.path.splitext(file_path)[0] + '.pkl'
            with open(file_path, 'wb') as f: 
                pickle.dump({
                    'targetName': self.targetName,
                    'model': self.modelData
                }, f)

    def openModel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Pickle (*.pkl)')
        if file_path:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.targetName = data['targetName']
                self.loadModel(data['model'])

    def exit_app(self):
        QApplication.quit()

    def open_repo(self):
        url = QUrl('https://www.github.com/atilmohamine/QSAR-Bioactivity-Predictor')
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, 'Open Url', 'Could not open url')    

    def show_about_dialog(self):
        self.AboutWindow = AboutWindow()
        self.AboutWindow.show()
    
    def loadCSV(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV Files (*.csv)')
        if file_path:
            df = pd.read_csv(file_path)
            self.PredictWindow = PredictWindow(self.modelData, df)
            self.PredictWindow.show()            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())