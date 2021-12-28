# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 17:45:24 2021

@author: Utente
"""


import pickle
import sys
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.append("../utility")
from utility.utils import pd, preprocessing


# Importing the dataset
DATASET_COLUMNS=['text', 'target']
DATASET_ENCODING = "ISO-8859-1"
data = pd.read_csv('dataset.tsv', encoding=DATASET_ENCODING, names=DATASET_COLUMNS, sep="\t")

data_pos = data[data['target'] == 1] #800k positive tweet
data_neg = data[data['target'] == 0] #800k negative tweet

#with next rows are selected 100k positive tweets and 100k negative tweets
data_pos = data_pos.iloc[:int(100000)] 
data_neg = data_neg.iloc[:int(100000)]

dataset = pd.concat([data_pos, data_neg])
processed_tweets = preprocessing(dataset['text'])

#TRAINING SET
X_train = processed_tweets.apply(lambda x: " ".join(x))
y_train = dataset.target

#148653 is the vocabulary size of the training_set
vectoriser = TfidfVectorizer(ngram_range=(1,2), max_features=148653)

#tf-idf vectorization of each tweet
X_train_matrix = vectoriser.fit_transform(X_train)

filename = "../models/TfIdfvectorizer_model.sav"
pickle.dump(vectoriser, open(filename, "wb"))
#print('No. of feature_words: ', len(vectoriser.get_feature_names()))


BNBmodel = BernoulliNB()
BNBmodel.fit(X_train_matrix, y_train)
filename = "../models/BNB_model.sav"
pickle.dump(BNBmodel, open(filename, "wb"))