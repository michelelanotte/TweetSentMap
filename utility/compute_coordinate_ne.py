# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 18:12:39 2021

@author: Utente
"""

from utility.utils import cleaningForNE, getNE, re, removeDuplicate, getCoordFromPlace, Heuristic


"""
This method is based on spacy to perform Named Entities Recognition
"""
def computeNamedPlaces(tweet):
    filters = ["PERSON", "TIME", "DATE", "ORDINAL", "MONEY", "WORK_OF_ART", "CARDINAL", "PRODUCT", "PERCENT", "EVENT"]
    entities = getNE(tweet, filters)       
    return entities


"""
This method excludes incorrect named entities from name_entities_list. 
Only one location will be returned for the current tweet. 
"""
def filteringNE(i, name_entities_list):
    ne_filtered = []
    for ne in name_entities_list:
        pattern_re = "\\x80.*|\\x98.*|\\x81.*|.\\x9f.*|.\\x9c.*|.\\x9d.*|.\\x99.*|@"
        ne = re.sub(pattern_re, ' ', ne).strip()
        if len(ne) > 1:
            ne_filtered.append(ne.lower())
    
    #removing duplicate
    res = removeDuplicate(ne_filtered)
        
    return res


"""
This method receives as input a list of tweets and for each one computes, through the NERSpacy, 
the places indicated therein. Starting from the detected places, the representative coordinate 
among all those computed is selected.
The method returns a list of coordinates, one for each tweet.
"""
def getCoordinates(tweets):
    coords = []
    for i, tweet in enumerate(tweets):
        #The removal of punctuation, double characters, url and tag was not considered, as there is an overall 
        #decrease in performance (in precision and recall)
        tweet_cleaned = cleaningForNE(tweet)
        print(i)
        #named_entities_list is a list of named entities detected in current tweet
        named_entities_list = computeNamedPlaces(tweet_cleaned)
        ne_filtered = filteringNE(i, named_entities_list)
        
        coords.append(getCoordFromPlace(tweet, ne_filtered, Heuristic.third))
    return coords