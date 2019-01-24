import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QLabel, QPushButton, QProgressBar, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from ember import PEFeatureExtractor
from ember import features
import ember
import jsonlines
import pandas as pd
import os
import tqdm

class App(QWidget): 
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.features = []

        self.initUI()

    def initUI(self):
        # trainsetLabel
        self.trainsetLabel = QLabel("trainset: ", self)
        self.trainsetLabel.move(20,20)

        # trainsetPathLabel
        self.trainsetPathLabel = QLabel("None", self)
        self.trainsetPathLabel.move(80,18)
        self.trainsetPathLabel.resize(500, 20)

        # Filedialog button
        self.TrainSetbutton = QPushButton('Open', self)
        self.TrainSetbutton.setToolTip('This is an example button')
        self.TrainSetbutton.move(20 ,40)
        self.TrainSetbutton.clicked.connect(self.TrainSetbutton_click)

        # trainset csv Label
        self.trainsetcsvLabel = QLabel("trainsetLabel: ", self)
        self.trainsetcsvLabel.move(20,80)

        # trainsetPathLabel
        self.trainsetcsvPathLabel = QLabel("None", self)
        self.trainsetcsvPathLabel.move(115,78)
        self.trainsetcsvPathLabel.resize(500, 20)

        # Filedialog button
        self.TrainSetCSVbutton = QPushButton('Open', self)
        self.TrainSetCSVbutton.setToolTip('This is an example button')
        self.TrainSetCSVbutton.move(20 ,100)
        self.TrainSetCSVbutton.clicked.connect(self.TrainSetcsvbutton_click)

        #Extract button
        self.extractBtn = QPushButton('Extract features', self)
        self.extractBtn.setToolTip('This is an example button')
        self.extractBtn.move(20 ,150)
        self.extractBtn.clicked.connect(self.extractBtn_click)

        #Progress bar
        self.progress = QProgressBar(self)
        self.progress.move(20, 400)
        self.progress.resize(600, 40)
        #self.setMaximum(100)

        # Checkbox on features for extracting
        # String
        self.FeStringChkBox = QCheckBox('features about string', self)
        self.FeStringChkBox.move(20, 200)
        self.FeStringChkBox.resize(500, 30)

        # ImportsInfo
        self.FeImportsChkBox = QCheckBox('features about ImportsInfo', self)
        self.FeImportsChkBox.move(20, 220)
        self.FeImportsChkBox.resize(500, 30)

        # byte histogram
        self.FeBytehistogramChkBox = QCheckBox('features about bytehistorgram', self)
        self.FeBytehistogramChkBox.move(20, 240)
        self.FeBytehistogramChkBox.resize(500, 30)

         # ByteEntropyHistogram
        self.FeByteEntropyHistogramChkBox = QCheckBox('features about byte-entropy historgram', self)
        self.FeByteEntropyHistogramChkBox.move(20, 260)
        self.FeByteEntropyHistogramChkBox.resize(500, 30)

        self.setWindowTitle('Malware detection using AI')
        self.setGeometry(self.left, self.top, self.width, self.height)
                
        self.show()
    
    # Button's event
    def TrainSetbutton_click(self):
        DirName = QFileDialog.getExistingDirectory(self, "Select Folder")
        if DirName:
            self.trainsetPathLabel.setText(DirName)

    def TrainSetcsvbutton_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*)", options=options)
        if fileName:
            self.trainsetcsvPathLabel.setText(fileName)
            
    # extract
    def extractBtn_click(self):
        data = pd.read_csv(self.trainsetcsvPathLabel.text(), names=['hash', 'y'])
        extractor = PEFeatureExtractor()

        ErrorCount = 0
        dirlists = os.listdir(self.trainsetPathLabel.text())
        end = len(dirlists)

        #features add
        self.features.clear()
        if self.FeStringChkBox.isChecked():
            self.features.append(features.StringExtractor())
        if self.FeImportsChkBox.isChecked():
            self.features.append(features.ImportsInfo())
        if self.FeBytehistogramChkBox.isChecked():
            self.features.append(features.ByteHistogram())
        if self.FeByteEntropyHistogramChkBox.isChecked():
            self.features.append(features.ByteEntropyHistogram())
        
        
        with jsonlines.open(os.path.join('output', "features.jsonl"), 'w') as f:
            for idx, _file in enumerate(dirlists):
                path = os.path.join(self.trainsetPathLabel.text(), _file)
                binary = open(path, 'rb').read()

                try:
                    feature = extractor.raw_features(binary, self.features)
                    feature.update({"sha256": _file}) #hash
                    feature.update({"label" : data[data.hash==_file].values[0][1]}) #label
                    f.write(feature)        
                except KeyboardInterrupt:
                    sys.exit()
                except Exception as e:
                    ErrorCount += 1
                    print(e)
                self.progress.setValue((idx+1)/end * 100)
                

        print("Error : %d" % (ErrorCount))
        print("Done")

    
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())