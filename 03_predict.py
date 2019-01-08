#!/usr/bin/env python
import os
import ember
import argparse
import lightgbm as lgb
import argparse
import tqdm
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--modelpath", type=str, required=True, help="trained model path")
    parser.add_argument("-d", "--datadir", type=str, help="Directory for predicting dataSets", required=True)
    parser.add_argument("-o", "--output", type=str, help="output label and y_pred", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.modelpath):
        parser.error("ember model {} does not exist".format(args.modelpath))   
    if not os.path.exists(args.datadir):
        parser.error("ember model {} does not exist".format(args.datadir))
    if not os.path.exists(args.output):
        os.mkdir(args.output)

    model_path = os.path.join(args.modelpath, "model.txt")
    lgbm_model = lgb.Booster(model_file=model_path)

    errorcount = 0
    y_pred = []
    _name = []

    for filename in tqdm.tqdm(os.listdir(args.datadir)):
        _file = os.path.join(args.datadir, filename)

        if os.path.isfile(_file):
            binary = open(_file, "rb").read()
            _name.append(filename)

            try:
                y_pred.append(ember.predict_sample(lgbm_model, binary))           
            except KeyboardInterrupt:
                sys.exit()
            except:
                y_pred.append(0)
                errorcount += 1
                
    #print and save accuracy
    y_pred_01 = np.array(y_pred)
    y_pred_01 = np.where(y_pred_01 > 0.7, 1, 0)   

    #save csv
    raw_predict = pd.DataFrame({'hash': _name, 'ypred': y_pred_01})
    raw_predict.to_csv(os.path.join(args.output, 'result.csv'), index=False, header=None)

    #print error count
    print("Error : %d" % (errorcount))
    
if __name__ == "__main__":
    main()
    print("Done")
