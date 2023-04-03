from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski
import numpy as np
import pandas as pd


class LipinskiCalculator:

    def calculate_descriptors(self, smiles):
        moldata= []
        for elem in smiles:
            mol=Chem.MolFromSmiles(elem) 
            moldata.append(mol)
        
        baseData= np.arange(1,1)
        i=0  
        for mol in moldata:        
        
            desc_MolWt = Descriptors.MolWt(mol)
            desc_MolLogP = Descriptors.MolLogP(mol)
            desc_NumHDonors = Lipinski.NumHDonors(mol)
            desc_NumHAcceptors = Lipinski.NumHAcceptors(mol)
            
            row = np.array([desc_MolWt,
                            desc_MolLogP,
                            desc_NumHDonors,
                            desc_NumHAcceptors])   
        
            if(i==0):
                baseData=row
            else:
                baseData=np.vstack([baseData, row])
            i=i+1      
        
        columnNames=["MW","LogP","NumHDonors","NumHAcceptors"]   
        descriptors = pd.DataFrame(data=baseData,columns=columnNames)
        
        return descriptors
