# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 11:30:30 2021

@author: Utente
"""

import os
from datetime import datetime
from utility.utils import dataFrameToTsv
from utility.sentiment_analysis import sentimentAnalysis
from utility.compute_coordinate_ne import getCoordinates
    

def update_sentiment_and_coordinate():
    #this file contains SOP tweets
    with open("dataset/tweets_dataset.txt", "r", encoding = "ISO-8859-1") as file:
        tweets = file.readlines()
    
    if tweets:
        #list of sentiments for each tweet
        sentiments = sentimentAnalysis(tweets)
        #list of coordinates for each tweet. Each coordinates element is of the form <latitude, longitude>
        coordinates = getCoordinates(tweets)
        dataset = zip(tweets, sentiments, coordinates)
        
        #this file contains triples <tweet, sentiment, coordinates> 
        with open("dataset/sentiments.tsv", "w", encoding = "ISO-8859-1") as tsv_file:
            dataFrameToTsv(dataset, tsv_file)
        

#DA RIMUOVERE LA RIGA 31!!!
update_sentiment_and_coordinate()

"""
last_update = datetime.fromtimestamp(os.path.getmtime("dataset/tweets_dataset.txt"))
while(True):
    new_last_update = datetime.fromtimestamp(os.path.getmtime("dataset/tweets_dataset.txt"))
    if new_last_update > last_update:
        update_sentiment_and_coordinate()
        last_update = new_last_update"""    
    
    
    