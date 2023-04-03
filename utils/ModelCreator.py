from PyQt5.QtCore import QThread, pyqtSignal
from chembl_webresource_client.new_client import new_client
import pandas as pd
import numpy as np
import subprocess
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold
from utils.LipinskiCalculator import LipinskiCalculator


class ModelCreator(QThread):

    progress = pyqtSignal(int)
    progressStatus = pyqtSignal(str)

    modelReady = pyqtSignal(object)

    def __init__(self, chemblId):
        super().__init__()
        self.chemblId = chemblId
        self.activity = new_client.activity
        
    def run(self):

        self.progressStatus.emit('Collect Activities')
        
        res = self.activity.filter(target_chembl_id=self.chemblId).filter(standard_type="IC50")
        df = pd.DataFrame.from_dict(res)

        # If any compounds has missing value for the standard_value and canonical_smiles column then drop it.
        df = df[df.standard_value.notna()]
        df = df[df.canonical_smiles.notna()]

        df = df.drop_duplicates(['canonical_smiles'])
        selection = ['molecule_chembl_id','canonical_smiles','standard_value']
        df = df[selection].reset_index(drop=True)

        # The bioactivity data is in the IC50 unit. 
        # Compounds having values of less than 1000 nM will be considered to be active while those greater than 10,000 nM will be considered to be inactive. 
        # As for those values in between 1,000 and 10,000 nM will be referred to as intermediate.

        self.progressStatus.emit('Calculate bioactivity data')
        self.progress.emit(10)

        bioactivity_threshold = []
        for i in df.standard_value:
            if float(i) >= 10000:
                bioactivity_threshold.append("inactive")
            elif float(i) <= 1000:
                bioactivity_threshold.append("active")
            else:
                bioactivity_threshold.append("intermediate")
        
        bioactivity_class = pd.Series(bioactivity_threshold, name='class')
        df = pd.concat([df, bioactivity_class], axis=1)
        
        # Calculate Lipinski descriptors
        self.progressStatus.emit('Calculate Lipinski descriptors')
        self.progress.emit(20)

        smiles = []
        for i in df.canonical_smiles.tolist():
            cpd = str(i).split('.')
            cpd_longest = max(cpd, key = len)
            smiles.append(cpd_longest)

        lipinski_calc = LipinskiCalculator()
        df_lipinski = lipinski_calc.calculate_descriptors(smiles)

        df = pd.concat([df,df_lipinski], axis=1)
        
        self.progressStatus.emit('Convert IC50 to pIC50')
        self.progress.emit(30)

        # Data normalization
        norm = []

        for i in df['standard_value']:
            if float(i) > 100000000:
                i = 100000000
            norm.append(i)

        df['standard_value_norm'] = norm
        df.drop('standard_value', 1)
                    
        # Convert IC50 to pIC50
        pIC50 = []

        for i in df['standard_value_norm']:
            molar = float(i)*(10**-9) # Converts nM to M
            pIC50.append(-np.log10(molar))

        df['pIC50'] = pIC50
        df.drop('standard_value_norm', 1)

        # Descriptor Calculation
        self.progressStatus.emit('Calculate fingerprint descriptors')
        self.progress.emit(40)

        df = df[df['class'] != 'intermediate']
        selection = ['canonical_smiles','molecule_chembl_id']
        df_selection = df[selection]
        df_selection.to_csv('./tmp/molecule.smi', sep='\t', index=False, header=False)

        bashCommand = "java -Xms1G -Xmx1G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./tmp/ -file ./tmp/descriptors_output.csv"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        process.wait()
        #output, error = process.communicate()

        # Dataset preparation
        self.progressStatus.emit('Dataset preparation')
        self.progress.emit(50)

        Xdf = pd.read_csv('./tmp/descriptors_output.csv')
        Xdf = Xdf.drop(columns=['Name'])
        Y = df['pIC50']
        
        # Remove low variance features
        selection = VarianceThreshold(threshold=(.8 * (1 - .8)))    
        X = selection.fit_transform(Xdf)

        # Get the Boolean mask indicating which columns were selected
        selected_mask = selection.get_support()

        # Index the original DataFrame with the mask to get the not removed columns
        selected_cols = Xdf.columns[selected_mask]

        # Training the model
        self.progressStatus.emit('Training the model')
        self.progress.emit(60)

        best_score = 0
        best_model = None
        training_times = 250
        best_X_train = best_X_test = best_Y_train = best_Y_test = None

        for i in range(training_times):
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
            model = RandomForestRegressor(n_estimators=100)
            model.fit(X_train, Y_train)
            score = model.score(X_test, Y_test)
            if score > best_score:
                best_score = score
                best_model = model
                best_X_train = X_train
                best_X_test = X_test
                best_Y_train = Y_train
                best_Y_test = Y_test

            self.progress.emit(int(60+((i*40)/training_times)))
        
        Y_pred = best_model.predict(best_X_test)

        # Defines and builds the lazyclassifier
        #clf = LazyRegressor(verbose=0,ignore_warnings=True, custom_metric=None)
        #models_train,predictions_train = clf.fit(X_train, X_train, Y_train, Y_train)
        #models_test,predictions_test = clf.fit(X_train, X_test, Y_train, Y_test)

        self.modelReady.emit({
            'model': best_model,
            'score': best_score,
            'X_train': best_X_train,
            'X_test': best_X_test,
            'Y_train': best_Y_train,
            'Y_test': best_Y_test,
            'Y_pred': Y_pred,
            'df': df,
            'selected_cols': selected_cols
        })
