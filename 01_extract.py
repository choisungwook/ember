# -*- coding:utf-8 -*-
import os
import argparse
import sys
from ember import PEFeatureExtractor
import tqdm
import jsonlines
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", help="Dataset path", required=True)
parser.add_argument("-o", "--output", help="output path", required=True)
parser.add_argument("-c", "--csv", help="dataset label", required=True)
args = parser.parse_args()

if not os.path.exists(args.dataset):
    parser.error("ember model {} does not exist".format(args.dataset))    
if not os.path.exists(args.csv):
    parser.error("ember model {} does not exist".format(args.csv))
if not os.path.exists(args.output):        
    os.mkdir(args.output)

data = pd.read_csv(args.csv, names=['hash', 'y'])

def ExtractLabel(filename):
    return data[data.hash==filename].values[0][1]
                    
def main():
    ErrorCount = 0
    extractor = PEFeatureExtractor()

    with jsonlines.open(os.path.join(args.output, "features.jsonl"), 'w') as f:
        for _file in tqdm.tqdm(os.listdir(args.dataset)):
            path = os.path.join(args.dataset, _file)
            try:
                feature = extractor.raw_features(path)
                
                feature.update({"sha256": _file}) #hash
                feature.update({"label" : ExtractLabel(_file)}) #label
                f.write(feature)        
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                ErrorCount += 1
                print('error')
    
if __name__=='__main__':
    pass