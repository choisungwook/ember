"""
This python module refer to Ember Porject(https://github.com/endgameinc/ember.git)
"""
import os
import argparse
import sys
import tqdm
import jsonlines
import pandas as pd
import multiprocessing
import lightgbm as lgb
import numpy as np
from ember import PEFeatureExtractor

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--modelpath", type=str, required=True, help="trained model path")
parser.add_argument("-d", "--datadir", type=str, help="Directory for predicting dataSets", required=True)
parser.add_argument("-c", "--csv", type=str, help="Answer file", required=True)
parser.add_argument("-o", "--output", type=str, help="output label and y_pred", required=True)
args = parser.parse_args()

if not os.path.exists(args.modelpath):
    parser.error("ember model {} does not exist".format(args.modelpath))   
if not os.path.exists(args.csv):
    parser.error("ember model {} does not exist".format(args.csv))
if not os.path.exists(args.datadir):
    parser.error("ember model {} does not exist".format(args.datadir))
if not os.path.exists(args.output):
    os.mkdir(args.output)

model_path = os.path.join(args.modelpath, "model.txt")
lgbm_model = lgb.Booster(model_file=model_path)

#read answer sheet
data = pd.read_csv(args.csv, names=['hash', 'y'])

def ExtractLabel(filename):
    """
    Get a label from filename(or hash)
    """
    return data[data.hash==filename].values[0][1]

"""
It may be not safe multiprocess.
Safe mechanism is to be line 87.
"""
def sample_iterator():
    """
    Os.listdir to iterator
    """
    for sample in os.listdir(args.datadir):
        yield sample

def predict(sample):
    """
    Predict new testdataset
    """
    extractor = PEFeatureExtractor()
    fullpath = os.path.join(os.path.join(args.datadir, sample))
    #model_path = os.path.join(args.modelpath, "model.txt")
    model = lgbm_model

    try:
        binary = open(fullpath, 'rb').read()
        features = np.array(extractor.feature_vector(binary), dtype=np.float32)
        #y_pred = model.predict([features])[0]
    except KeyboardInterrupt:
        print('Input keyboard interrupt')
        sys.exit()
    except Exception as e:        
        print("{}: {} error is occuered. A predict value set 0".format(sample, e))
        y_pred = 0
    lgbm_model.predict([features])[0]
    # r = {}
    # r['sample'] = sample
    # r['y_pred'] = y_pred
    # r['label'] = ExtractLabel(sample)
    
    #return r

def predict_unpack(args):
    """
    Pass thorugh function unpacking arguments
    """
    return predict(args)

def predict_subset():
    """
    Ready to do multi Process
    Note that total variable in tqdm.tqdm should be revised
    Currently, I think that It is not safely. Because, multiprocess pool try to do FILE I/O.
    """
    error = 0
    pool = multiprocessing.Pool(1)
    queue = multiprocessing.Queue()
    queue.put('safe')
    
    predict_iterator = (sample for idx, sample in enumerate(sample_iterator()))
    
    
    y_pred = []
    name = []
    y = []
    for _ in tqdm.tqdm(pool.imap_unordered(predict_unpack, predict_iterator), total=10000):
        pass
        # msg = queue.get()
        # if msg == 'safe': 
        #     sample = x['sample']
        #     pred = x['y_pred']
        #     answer = x['label']

        #     y.append(answer)
        #     y_pred.append(pred)
        #     name.append(sample)

        #     queue.put('safe')
        
    pool.close()

    # #print and save accuracy
    # y_pred_01 = np.array(y_pred)
    # y_pred_01 = np.where(y_pred_01 > 0.7, 1, 0)   

    # #save csv
    # raw_predict = pd.DataFrame({'hash': name, 'y': y, 'ypred': y_pred_01})
    # raw_predict.to_csv(os.path.join(args.output, 'predict_with_label.csv'), index=False, header=None)

    # r = pd.DataFrame({'hash': name, 'y_pred': y_pred_01})
    # r.to_csv(os.path.join(args.output, 'result.csv'), index=False, header=None)


def main():
    # Extract features using the multiprocess pool
    predict_subset()
    #print('error is occuered {}'.format(error))

    """
    Another options to try multiprocess. 
    But, it is not completed.
    """
    # lists = os.listdir(args.dataset)
    # pool = ProcessPoolExecutor(max_workers=6)
    # for _ in tqdm.tqdm(pool.map(extract_features_processpool, lists), total=10000):
    #     pass
    
if __name__=='__main__':
    main()

"""
Try do ProcessPoolExecutor of multiprocess.
Currently, it is not used.
"""
# def extract_features_processpool(path):
#     """
#     Extract features
#     """
#     extractor = PEFeatureExtractor()
#     fullpath = os.path.join(args.dataset, path)
#     binary = open(fullpath, 'rb').read()

#     try:
#         feature = extractor.raw_features(binary)
#     except KeyboardInterrupt:
#         print('Keyboard interrupt is occured')
#         sys.exit()
#     except Exception as e:
#         print("{}: {}".format(fullpath, e))
#         return None

#     return feature