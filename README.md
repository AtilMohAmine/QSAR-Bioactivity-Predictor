# QSAR Bioactivity Predictor
QSAR Bioactivity Predictor is a Python application that allows users to create QSAR models to predict bioactivity for a specific target.

<p align="center"><img src="https://user-images.githubusercontent.com/86023602/229597174-c3f4e2b4-8c86-4a21-a025-9be3fbea6f6a.png" width="600px" /></p>

## Installation
To use QSAR-Bioactivity-Predictor, you need to have Python 3.x installed on your system. You also need to install the following Python packages:
- chembl-webresource-client==0.10.8
- numpy==1.24.2
- pandas==1.5.3
- PyQt5==5.15.9
- PyQt5-Qt5==5.15.2
- rdkit==2022.9.5
- scikit-learn==1.2.2
- seaborn==0.12.2

You can install these packages using pip by running the following command:
```sh
  $ pip install -r requirements.txt
```

## Usage
To run the QSAR-Bioactivity-Predictor application, open a terminal window and navigate to the directory where the qsar-predictor.py file is located. Then, run the following command:

```sh
  $ python qsar-predictor.py
```

This will open the main window of the application, where you can select a target and create a QSAR model to predict bioactivity for that target.

## Features
The QSAR-Bioactivity-Predictor application provides the following features:
- Load data using Chembl webresource client containing molecular descriptors and bioactivity values for a specific target.

<p align="center"><img src="https://user-images.githubusercontent.com/86023602/229595709-ad887bde-a643-4375-8611-030409be339a.png" width="500px" /></p>

- Preprocess the data by removing missing values and normalizing the descriptors.
- Train a QSAR model using random forest regressor
- Plot the experimental versus predicted pIC50 values.
- Predict pIC50 values of input SMILES CSV.
<p align="center"><img src="https://user-images.githubusercontent.com/86023602/229595826-02639cc3-57b2-434c-9213-31e778986699.png" /></p>

- Save the model to a file for later use.

## Contributing
If you want to contribute to QSAR-Bioactivity-Predictor, feel free to fork the repository and submit a pull request with your changes.

## License
QSAR-Bioactivity-Predictor is licensed under the MIT License. See the [LICENSE](https://github.com/AtilMohAmine/QSAR-Bioactivity-Predictor/blob/main/LICENCE) file for more information.

## Acknowledgments
- The QSAR Bioactivity Predictor application was developed as a final project for a Master's degree.
- The application uses the PaDEL-Descriptor to calculate molecular descriptors from chemical structures.
- The QSAR models were trained using the scikit-learn library.
