# State Change
1. ember/features.py: change row variables -2018.10  
2. remove resource directory -2018.10  
3. change script files -2018.10  
4. add 01_extract.py, 02_train.py, 03_predict.py, 04_get_accuracy.py  -2018.10   
(this refer to ember/init.py, ember/features.py)
5. add utils directory  -2018.10 
6. add Test directory  -2018.10 
7. add output directory -2018.12   
8. add multiprocess job of extracting freature - 2019.01
9. Failed to develop multiprocess predcit. The AI framework developer ban it. - 2019.01
<br />
<br />
# Reference
https://github.com/endgameinc/ember  

H. Anderson and P. Roth, "EMBER: An Open Dataset for Training Static PE Malware Machine Learning Models”, in ArXiv e-prints. Apr. 2018.  

```
@ARTICLE{2018arXiv180404637A,  
  author = {{Anderson}, H.~S. and {Roth}, P.},  
  title = "{EMBER: An Open Dataset for Training Static PE Malware Machine Learning Models}",  
  journal = {ArXiv e-prints},  
  archivePrefix = "arXiv",  
  eprint = {1804.04637},  
  primaryClass = "cs.CR",  
  keywords = {Computer Science - Cryptography and Security},  
  year = 2018,  
  month = apr,  
  adsurl = {http://adsabs.harvard.edu/abs/2018arXiv180404637A},  
}  
```  
  
# Install
Above python 3.6.8  

```
sudo apt install python-pip3
```

```
;Install virtualenv
$ virtualenv env -p python3
$ . ./env/bin/activate
```
  
```
;Install python modules
(env)$ pip3 install -r requirements.txt
```

# Prerequisite
* inputfile(csv including label) structure without column's names  

![traindata_label](screenshot/traindata_label.png)

# how to Run
## Progress
1. 01_extract.py or 01_extract_multi.py 
2. 02_train.py
3. 03_predict.py 
4. 04_get_accuracy.py 

## Detail
1. extract features from trainsets  
If you run, jsonl file is created.
```
(env)python 01_extract.py -d [TrainSet path] -c [TrainSet label path] -o [output path]
```
<br />  

If you want to mulitprocess, try 01_extract_multi.py.   
My computer is I7-8700 and not use Graphic card.    
When I use 01_extract_multi.py, It is faster 1500% than 01.extract.py    

<br /> 

* Note that you must change number of processor and number of trainsets  
```
82: pool = multiprocessing.Pool(number of processor)

88: for x in tqdm.tqdm(pool.imap_unordered(extract_unpack, extractor_iterator), total=number of trainsets):
```

```
(env)python 01_extract_multi.py -d [TrainSet path] -c [TrainSet label path] -o [output path]
```

<br /> 

2. train.py  

```
(env) python 02_train.py -d [jsonl path] -o [output path]
``` 

3. 03_predict.py
```
(env) python 03_predict.py -m [model.txt path] -d [testdataset path] -o [output path]
```
<br />  
4. 04_get_accuracy.py
```
(env) python 04_get_accuracy.py -c [result of 03_predict.py path] -l [tesdataset label path]
```
<br />

## To Do
1. Pipelien from scikit-learn.  
2. GUI or web UI.  
3. guide videos.  
4. 01_extract_multi.py auto setting.  
5. K-Fold evaluation  
<br />  
<br />  

# Screenshot of run 

* 01_extract.py
<br /> 

![extract.py](screenshot/01_extract_multi.png)  

* 03_predict.py
<br /> 

![predict.py](screenshot/03_predict.png)  

<br /> 

* 04_get_accuracy.py  

![get_accuracy.py](screenshot/04_get_accuracy.png)  
