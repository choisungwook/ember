"""
This python module refer to Ember Porject(https://github.com/endgameinc/ember.git)
"""
import os
import argparse
import sys
from ember import PEFeatureExtractor
import tqdm
import jsonlines
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

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
    for sample in os.listdir(args.dataset):
        yield sample

def extract_features(sample, output):
    """
    Extract features.
    If error is occured, return None Object
    """
    extractor = PEFeatureExtractor()
    fullpath = os.path.join(os.path.join(args.dataset, sample))
    try:
        binary = open(fullpath, 'rb').read()
        feature = extractor.raw_features(binary)
        feature.update({"sha256": sample}) # sample name(hash)
        feature.update({"label" : ExtractLabel(sample)}) #label

    except KeyboardInterrupt:
        print('Input keyboard interrupt')
        sys.exit()
    except Exception as e:        
        print("{}: {} error is occuered".format(sample, e))
        return None

    return feature
       
def extract_unpack(args):
    """
    Pass thorugh function unpacking arguments
    """
    return extract_features(*args)

def extract_subset():
    """
    Ready to do multi Process
    Note that total variable in tqdm.tqdm should be revised
    Currently, I think that It is not safely. Because, multiprocess pool try to do FILE I/O.
    """
    error = 0
    pool = multiprocessing.Pool(4)
    queue = multiprocessing.Queue()
    queue.put('safe')
    end = len(next(os.walk(args.dataset))[2])
    
    extractor_iterator = ((sample, os.path.join(args.output, 'features.jsonl')) for idx, sample in enumerate(sample_iterator()))
    with jsonlines.open(os.path.join(args.output, "features.jsonl"), 'w') as f:
        for x in tqdm.tqdm(pool.imap_unordered(extract_unpack, extractor_iterator), total=end):
            if not x:
                """
                To input error class or function
                """
                error += 1
                continue
            msg = queue.get()
            if msg == 'safe': 
                f.write(x)                
                queue.put('safe')
            
    pool.close()

    return error

def main():
    # Extract features using the multiprocess pool
    error = extract_subset()
    print('error is occuered {}'.format(error))

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
