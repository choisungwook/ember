import unittest
import pandas as pd
import os
import sys
import jsonlines
import tqdm
import lightgbm as lgb
import pefile
from collections import OrderedDict

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from ember import PEFeatureExtractor, create_vectorized_features, train_model, predict_sample

def ExtractLabel(filename, df):
    return df[df.hash==filename].values[0][1]

def sample_iterator(dirpath):
    '''
    디렉터리 탐색 제너레이터
    '''
    for filename in os.listdir(dirpath):
        yield filename

class TestArea(unittest.TestCase):
    def setUp(self):
        '''
        테스트 초기화
        '''
        self.dirpath = 'C:\\Users\\sungwook\\Documents\\dataset\\TrainTest'
        self.output = 'C:\\Users\\sungwook\\Documents\\dataset'
        self.csv = 'C:\\Users\\sungwook\\Documents\\dataset\\TrainSet.csv'
        self.testdirpath = 'C:\\Users\\sungwook\\Documents\\dataset\\TestTest'

    def test_extract_features(self):
        '''
        특성 추출 테스트
        '''        
        df = pd.read_csv(self.csv, names=['hash', 'y'])
        extractor = PEFeatureExtractor()

        # 파일 쓰기
        with jsonlines.open(os.path.join(self.output, "features.jsonl"), 'w') as f:
            for _file in tqdm.tqdm(os.listdir(self.dirpath)):
                path = os.path.join(self.dirpath, _file)
                try:
                    feature = extractor.raw_features(path)
                    
                    feature.update({"sha256": _file}) #hash
                    feature.update({"label" : ExtractLabel(_file, df)}) #label
                    f.write(feature)        
                except KeyboardInterrupt:
                    sys.exit()
                except Exception as e:
                    print('{} has error: {}'.format(_file, e))

    def test_train_model(self):
        '''
        모델 학습 테스트
        '''
        rows = 0
        with jsonlines.open(os.path.join(self.output, 'features.jsonl')) as reader:
            for obj in reader.iter(type=dict, skip_invalid=True):
                rows += 1

        # 벡터화
        create_vectorized_features(self.output, rows)

        # Train and save model
        print("Training LightGBM model")
        lgbm_model = train_model(self.output, rows)
        lgbm_model.save_model(os.path.join(self.output, "model.txt")) 


    def test_predict_sample_withModel(self):
        '''
        학습한 모델을 사용해서 샘플 예측 테스트
        '''
        model_path = os.path.join(self.output, "model.txt")
        lgbm_model = lgb.Booster(model_file=model_path)

        y_pred = []
        name = []
        err = 0
        end = len(next(os.walk(self.testdirpath))[2])

        for filename in tqdm.tqdm(sample_iterator(self.testdirpath), total=end):
            filepath = os.path.join(self.testdirpath, filename)
            name.append(filename)
            try:
                y_pred.append(predict_sample(lgbm_model, filepath))
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                y_pred.append(0)
                print("{}: {} error is occuered".format(filename, e))
                err += 1
                    
        series = OrderedDict([('hash', name),('y_pred', y_pred)])
        r = pd.DataFrame.from_dict(series)
        r.to_csv(os.path.join(self.output, 'result.csv'), index=False, header=None)