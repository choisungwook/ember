import argparse
import os
from ember import features
import ember
import sys
import subprocess
import jsonlines

def clear(data_dir):
	path_X = os.path.join(data_dir, "X.dat")
	path_y = os.path.join(data_dir, "y.dat")

	if os.path.isfile(path_X):
		os.remove(path_X)
	if os.path.isfile(path_y):
		os.remove(path_y)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--datadir", help="Features Directory", type=str)
	parser.add_argument("-o", "--output", help="output Directory", type=str)
	args = parser.parse_args()

	if not os.path.exists(args.datadir):
		parser.error("{} is not a directory".format(args.datadir))
	if not os.path.exists(args.output):
		os.mkdir(args.output)

	#Get total lines from feature.jsonl
	rows = 0
	with jsonlines.open(os.path.join(args.datadir, 'features.jsonl')) as reader:
		for obj in reader.iter(type=dict, skip_invalid=True):
			rows += 1

	clear(args.datadir)
	ember.create_vectorized_features(args.datadir, rows)

	# Train and save model
	print("Training LightGBM model")
	lgbm_model = ember.train_model(args.datadir, rows)
	lgbm_model.save_model(os.path.join(args.output, "model.txt")) 

if __name__=='__main__':
	main()
	print("Done")
