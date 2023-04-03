from PyQt5.QtWidgets import QPushButton, QTableView, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSignal
from chembl_webresource_client.new_client import new_client
import pandas as pd
from utils import PandasModel

class SelectionWindow(QWidget):
    
    targetSignal = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Target selection')

        # Create a QLineEdit object for the search input
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText('coronavirus')

        self.SearchButton = QPushButton('Search', self)
        self.SearchButton.clicked.connect(self.search)

        self.selectedTarget = QLabel()
        self.SelectButton = QPushButton('Select', self)
        self.SelectButton.clicked.connect(self.select)

         # Create a QHBoxLayout object for the search widgets
        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.searchInput)
        searchLayout.addWidget(self.SearchButton)

        selectLayout = QHBoxLayout()
        selectLayout.addWidget(self.selectedTarget)
        selectLayout.addWidget(self.SelectButton)

        self.target = new_client.target
        target_query = self.target.search('coronavirus')
        self.df = pd.DataFrame.from_dict(target_query)

        self.table_view = QTableView()

        # Set the DataFrame to the table view
        self.table_view.setModel(PandasModel(self.df))

        # Connect the clicked signal of the table view to a method
        self.table_view.clicked.connect(self.on_table_clicked)

        self.chemblId = None

        layout = QVBoxLayout()
        self.label = QLabel("Enter target name")
        layout.addWidget(self.label)
        layout.addLayout(searchLayout)
        layout.addWidget(self.table_view)
        layout.addLayout(selectLayout)
        self.setLayout(layout)

    def search(self):
        try: 
            target_query = self.target.search(self.searchInput.text())
            self.df = pd.DataFrame.from_dict(target_query)
            self.df.drop(columns=self.df.columns[0], axis=1, inplace=True)
            # Set the DataFrame to the table view
            self.table_view.setModel(PandasModel(self.df))
        except: pass

    def select(self):
        if self.chemblId == None:
            QMessageBox.warning(self, 'Select target', 'Select target first') 
            return
        self.targetSignal.emit({
            'chemblId': self.chemblId,
            'targetName': self.targetName
            })
        self.close()

    def on_table_clicked(self, index):
        # Get the row and column of the clicked cell
        row = index.row()

        # Retrieve the data from the selected row in the DataFrame
        self.targetName = self.df.loc[row, 'pref_name']
        self.chemblId = self.df.loc[row, 'target_chembl_id']

        self.selectedTarget.setText('You are selected: {target}'.format(target = self.targetName))

        