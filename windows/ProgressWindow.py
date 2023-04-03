from PyQt5.QtWidgets import QWidget, QProgressBar, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal
from utils import ModelCreator

class ProgressWindow(QWidget):

    modelReady = pyqtSignal(object)

    def __init__(self, chemblId):
        super().__init__()

        self.chemblId = chemblId
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Progress')

        # Create a QLabel object for the status message
        self.statusLabel = QLabel()

        # Create a QProgressBar object
        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        # Create a QHBoxLayout object for the button and status label
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.statusLabel)

        # Create a QVBoxLayout object for the progress widget
        layout = QVBoxLayout()
        layout.addWidget(self.progressBar)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        self.startTask()

    def startTask(self):
        # Start the background task in a separate thread
        self.thread = ModelCreator(self.chemblId)
        self.thread.progress.connect(self.updateProgress)
        self.thread.progressStatus.connect(self.updateProgressStatus)
        self.thread.modelReady.connect(self.taskFinished)
        #self.thread.finished.connect(self.taskFinished)
        self.thread.start()

    def updateProgressStatus(self, value):
        self.statusLabel.setText(value)

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def taskFinished(self, data):
        self.statusLabel.setText('Task complete.')
        self.modelReady.emit(data)
        self.close()