from sklearn.metrics import confusion_matrix, accuracy_score
import pandas as pd
import numpy as np
import argparse
import os

np.set_printoptions(suppress=True)
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--csv', type=str, required=True, help='predicted csv file')
parser.add_argument('-l', '--label', type=str, required=True, help='csv file(label)')
parser.add_argument('-t', '--threshold', type=str, default=0.75, help='threadshold for predicting')
parser.add_argument('-o', '--output', default=None, help="save [option]")
args = parser.parse_args()

def main():
    data = pd.read_csv(args.csv, names=['hash', 'ypred'])
    label = pd.read_csv(args.csv, names=['hash', 'y'])

    y = label.y
    ypred = data.ypred
    #ypred = np.where(np.array(data.ypred) > args.threshold, 1, 0)

    #get and print accuracy
    accuracy = accuracy_score(y, ypred)
    print("accuracy : %.0f%%" % (np.round(accuracy, decimals=2)*100))
   
    tn, fp, fn, tp = confusion_matrix(y, ypred).ravel()
    mt = np.array([[tp, fp],[fn, tn]])

    print(mt)
    print("false postive rate : %.2f%%" % ( round(fp / float(fp + tn), 4) * 100))
    print("false negative rate : %.2f%%" % ( round(fn / float(fn + tp), 4) * 100))

    #save accuracy, mt [option]
    if args.output:
        with open(os.path.join(args.output, 'accuarcy.txt'), 'w') as f:
            accuracy.tofile(f, format='%s', sep='str')
        np.savetxt(os.path.join(args.output, 'matrix.txt'), mt)

if __name__=='__main__':
    main()
