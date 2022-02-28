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
DATASET_COLUMNS=['id', 'text', 'target']
DATASET_ENCODING = "ISO-8859-1"
datase = pd.read_csv('dataset.tsv', encoding=DATASET_ENCODING, names=DATASET_COLUMNS, sep="\t")

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