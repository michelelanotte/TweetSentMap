# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 11:30:30 2021

@author: Utente
"""

import os
import pandas as pd
from datetime import datetime
import time
from utility.utils import dataFrameToTsv
from utility.sentiment_analysis import sentimentAnalysis
from utility.compute_coordinate_ne import getCoordinates
from utility.utils import getDataframeByCity, readMidpoint_and_Bbox, splitTweetsBySentiment
from utility.pageRankTFIDF import computeTextRank


def compute_meaninful_tweets():
    dataset = pd.read_csv("dataset/sentiments_and_coords.tsv", sep = "\t", encoding = "ISO-8859-1", header = 0)   
    #compute text rank for cities
    dict_coordinates_midpoint, dict_coordinates_bbox = readMidpoint_and_Bbox("dataset/coords_localities.tsv")
    meaningful_tweets_positive_list = list()
    meaningful_tweets_negative_list = list()
    for city in dict_coordinates_midpoint.keys():
        dataframe_for_city = getDataframeByCity(city, pd.DataFrame(dataset), dict_coordinates_bbox)
        
        tweets_positive, tweets_negative = splitTweetsBySentiment(dataframe_for_city)
        embedding_model_filename = "models/TfIdfvectorizer_model.sav"
        meaningful_tweets_positive = computeTextRank(tweets_positive, embedding_model_filename)
        meaningful_tweets_negative = computeTextRank(tweets_negative, embedding_model_filename)
        meaningful_tweets_positive_list.append(meaningful_tweets_positive)
        meaningful_tweets_negative_list.append(meaningful_tweets_negative)
    
    tweets_rank_df = zip(dict_coordinates_midpoint.keys(), meaningful_tweets_positive_list, meaningful_tweets_negative_list)
    with open("dataset/meaningful_tweets.tsv", "w", encoding = "ISO-8859-1") as tsv_file:
        columns_name = ["City", "Meaningful positive", "Meaningful negative"]
        dataFrameToTsv(tweets_rank_df, tsv_file, columns_name)   


def update_sentiment_and_coordinate():
    columns_name = ["Tweet", "Sentiment", "Coordinate"]
    
    #this file contains SOP tweets
    with open("dataset/tweets_dataset.txt", "r", encoding = "ISO-8859-1") as file:
        tweets = file.readlines()
    
    if tweets:
        #list of sentiments for each tweet
        """sentiments = sentimentAnalysis(tweets)
        #list of coordinates for each tweet. Each coordinates element is of the form <latitude, longitude>
        coordinates = getCoordinates(tweets)
        dataset = zip(tweets, sentiments, coordinates)
        
        #this file contains triples <tweet, sentiment, coordinates> 
        with open("dataset/sentiments_and_coords.tsv", "w", encoding = "ISO-8859-1") as tsv_file:
            dataFrameToTsv(dataset, tsv_file, columns_name)"""
        
        compute_meaninful_tweets()    
        

#DA RIMUOVERE LA RIGA 36!!!
update_sentiment_and_coordinate()

"""
last_update = datetime.fromtimestamp(os.path.getmtime("dataset/tweets_dataset.txt"))
while(True):
    new_last_update = datetime.fromtimestamp(os.path.getmtime("dataset/tweets_dataset.txt"))
    if new_last_update > last_update:
        update_sentiment_and_coordinate()
        last_update = new_last_update
    time.sleep(60)
"""    
    
    
    