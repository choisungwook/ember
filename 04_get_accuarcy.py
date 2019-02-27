"""
you can evaulate the predict result If you have a label(answer) file.
Compare predict file and label(answer) file.

Thresdhold(args.threshold) change the predict score.
Default value of threshold is 0.7

Save options is not completed. I will save the data to confusion_matrix picture.
"""
from sklearn.metrics import confusion_matrix, accuracy_score
import pandas as pd
import numpy as np
import argparse
import tqdm
import os

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--csv', type=str, required=True, help='csv file(test result)')
parser.add_argument('-l', '--label', type=str, required=True, help='csv file(testdataset label)')
parser.add_argument('-t', '--threshold', type=str, default=0.5, help='threadshold for predicting')
args = parser.parse_args()

def main():
    data = pd.read_csv(args.csv, names=['hash', 'y_pred']).sort_values(by=['hash'])
    label = pd.read_csv(args.label, names=['hash', 'y']).sort_values(by=['hash'])
    end = len(data)
    y = []

    if len(label) == end:
        try:
            for idx, row in tqdm.tqdm(data.iterrows(), total=end):
                _name = row['hash']
                r = label[label.hash==_name].values[0][1]
                y.append(r)

            ypred = np.where(np.array(data.y_pred) > float(args.threshold), 1, 0)
 
            #get and print accuracy
            accuracy = accuracy_score(y, ypred)
            print("accuracy : %.2f%%" % (np.round(accuracy, decimals=4)*100))
        
            #get and print matrix
            tn, fp, fn, tp = confusion_matrix(y, ypred).ravel()
            mt = np.array([[tp, fp],[fn, tn]])

            print(mt)
            print("false postive rate : %.2f%%" % ( round(fp / float(fp + tn), 4) * 100))
            print("false negative rate : %.2f%%" % ( round(fn / float(fn + tp), 4) * 100))

        except:
            print("[Error] Please Check label file ****** ")
            
    else:
        print("[Error] Please Check label file ****** ")

if __name__=='__main__':
    main()
