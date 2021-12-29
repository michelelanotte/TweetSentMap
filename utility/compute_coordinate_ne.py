# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 18:12:39 2021

@author: Utente
"""

from utility.utils import cleaningForNE, getNE    

#This method is based on spacy to perform Named Entities Recognition
def computeNamedPlaces(tweet):
    filters = ["PERSON", "TIME", "DATE", "ORDINAL", "MONEY", "WORK_OF_ART", "CARDINAL", "PRODUCT", "PERCENT", "EVENT"]
    entities = getNE(tweet, filters)       
    return entities


def getCoordinates(tweets):
    coords = []
    for tweet in tweets:
        #The removal of punctuation, double characters, url and tag was not considered, as there is an overall 
        #decrease in performance (in precision and recall)
        tweet = cleaningForNE(tweet)
        #named_entities_list is a list of named entities detected in current tweet
        named_entities_list = computeNamedPlaces(tweet)
        print(named_entities_list)
        coords.append((0, 0))
    return coords