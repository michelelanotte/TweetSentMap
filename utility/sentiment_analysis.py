# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 16:57:41 2021

@author: Utente
"""

import pickle
from utility.utils import *


"""This method computes its vector shape for each tweet"""
def getVectors(processed_tweets):
    filename = "models/TfIdfvectorizer_model.sav"
    vectoriser = pickle.load(open(filename, 'rb'))
    vecs = vectoriser.transform(processed_tweets.apply(lambda x: " ".join(x)))
    return vecs
    

def sentimentAnalysis(tweets):
    #processed_tweets is a DataSeries in which each element is a sequence of tokens
    processed_tweets = preprocessing(tweets)
    #vecs is a list in which each element is a vector rapresentation of a tweet
    vecs = getVectors(processed_tweets)

    BNBmodel = pickle.load(open("models/BNB_model.sav", 'rb'))
    sentiments = BNBmodel.predict(vecs)
    
    #if prediction is 1, then sentiment for tweet is positive, else it's negative
    return ["POSITIVE" if s == 1 else "NEGATIVE" for s in sentiments]