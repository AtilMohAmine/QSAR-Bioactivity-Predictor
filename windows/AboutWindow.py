from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        self.initUI()

    def initUI(self):
        about_label = QLabel("QSAR Bioactivity Predictor v1.0\n\nThis application was developed by Atil Mohamed El Amine as a final project for my Master's degree. The source code is available on GitHub at:\n\nhttps://github.com/atilmohamine/QSAR-Bioactivity-Predictor")
        about_label.setFixedWidth(300)
        about_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(about_label)
        self.setLayout(layout)