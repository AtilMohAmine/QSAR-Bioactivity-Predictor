from PyQt5.QtWidgets import QTableView, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox
from utils import PandasModel
import subprocess
import pandas as pd
import os

class PredictWindow(QWidget):

    def __init__(self, modelData, df):
        super().__init__()
        self.setWindowTitle('Predict')
        self.setGeometry(100, 100, 300, 300)

        self.model = modelData['model']
        self.selected_cols = modelData['selected_cols']
        self.df = df
        self.df_predict = pd.DataFrame()

        self.table_view = QTableView()
        self.ExportButton = QPushButton('Export as CSV', self)
        self.ExportButton.clicked.connect(self.export)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        layout.addWidget(self.ExportButton)
        self.setLayout(layout)
        self.predict()

    def predict(self):
        self.df.to_csv('./tmp/molecule.smi', sep = '\t', header = False, index = False)

        bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./tmp/ -file ./tmp/descriptors_output.csv"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        process.wait()

        desc = pd.read_csv('./tmp/descriptors_output.csv')
        desc = desc.loc[:, self.selected_cols]
        
        Y_pred = self.model.predict(desc.values)

        prediction_output = pd.Series(Y_pred, name='pIC50')
        smiles = pd.Series(self.df.iloc[:, 0], name='SMILES')

        self.df_predict = pd.concat([smiles, prediction_output], axis=1)

        # Set the DataFrame to the table view
        self.table_view.setModel(PandasModel(self.df_predict))

    def export(self):
        if self.df_predict.empty:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV file", "", "CSV Files (*.csv)")
        if file_path:
            file_path = os.path.splitext(file_path)[0] + '.csv'
            self.df_predict.to_csv(file_path, index=False)
            # Show a success message in a dialog box
            message_box = QMessageBox()
            message_box.setWindowTitle("Success")
            message_box.setText(f"Data saved to {file_path}")
            message_box.setIcon(QMessageBox.Information)
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()