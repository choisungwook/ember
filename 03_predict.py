import os
import sys
import tqdm
import ember
import argparse
import numpy as np
import pandas as pd
import lightgbm as lgb
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--modelpath", type=str, required=True, help="trained model path")
parser.add_argument("-d", "--datadir", type=str, help="Directory for predicting dataSets", required=True)
parser.add_argument("-o", "--output", type=str, help="output directory", required=True)
args = parser.parse_args()

if not os.path.exists(args.modelpath):
    parser.error("ember model {} does not exist".format(args.modelpath))   
if not os.path.exists(args.datadir):
    parser.error("ember model {} does not exist".format(args.datadir))
if not os.path.exists(args.output):
    os.mkdir(args.output)

model_path = os.path.join(args.modelpath, "model.txt")
lgbm_model = lgb.Booster(model_file=model_path)

def predict():
    """
    Predcit new datasets
    """
    y_pred = []
    name = []
    err = 0
    end = len(next(os.walk(args.datadir))[2])

    for sample in tqdm.tqdm(sample_iterator(), total=end):
        fullpath = os.path.join(args.datadir, sample)

        if os.path.isfile(fullpath):
            binary = open(fullpath, "rb").read()
            name.append(sample)

            try:
                y_pred.append(ember.predict_sample(lgbm_model, binary))           
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                y_pred.append(0)
                print("{}: {} error is occuered".format(sample, e))
                err += 1
                
    series = OrderedDict([('hash', name),('y_pred', y_pred)])
    r = pd.DataFrame.from_dict(series)
    r.to_csv(os.path.join(args.output, 'result.csv'), index=False, header=None)

    return err

def sample_iterator():
    """
    Os.listdir to iterator
    """
    for sample in os.listdir(args.datadir):
        yield sample

def main():
    err = predict()
    print("Error is occured {}".format(err))
    
if __name__ == "__main__":
    main()
    print("Done")
