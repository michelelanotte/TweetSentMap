# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 12:14:30 2021

@author: Utente
"""

import pandas as pd
import re
import spacy
import string
import nltk
from nltk.tokenize import word_tokenize
from geopy import Nominatim
import geocoder
from enum import Enum
  

#heuristic used for coordinates selection. Permitted values: 1, 2, 3
class Heuristic(Enum):
    first = 1
    second = 2
    third = 3
    

#stop_words = set(stopwords.words('english'))
nlp = spacy.load("en_core_web_sm")

BING_KEY = "AjttQre1RsLFdGceLZYGGUWx0f3NY3ZyJiUU7tbTtWalvxVhSXhGH1kd1mMh0KzB"


"""
This method returns list of hastag in tweet.
"""
def getHastags(tweet):
    res = []
    if "#" in tweet:
        pattern_re = "#\w+"
        res = re.findall(pattern_re, tweet)
    return res


"""
This method removes the coordinates of places that contain other places. 
This way only the most specific places will be kept.
The method returns the list of filtered places and their respective coordinates.

Example: San Francisco is contained in California. The method returns San Francisco
"""
def prefilteringCoordinates(places, coord_couples, coord_bbox):
    new_coord_list = []
    candidate_places = []
    for i, bbox1 in enumerate(coord_bbox):
        contain_places = False
        
        #check if bbox1 contain another bbox
        for j, bbox2 in enumerate(coord_bbox):
            if i != j:             
                #It's verified that the bbox2 has latitudes between the latitudes of bbox1
                if bbox1[0][0] <= bbox2[0][0] and bbox2[0][1] <= bbox1[0][1]:
                    #It's verified that the bbox2 has longitudes between the longitudes of bbox1
                    if bbox1[1][0] <= bbox2[1][0]  and bbox2[1][1] <= bbox1[1][1]:
                        contain_places = True
                        break
                    
        #If the i-th bbox does not contain places, then the i-th coordinates are added to the output list
        if not contain_places:
            new_coord_list.append(coord_couples[i])
            candidate_places.append(places[i])
    return candidate_places, new_coord_list


def sendRequestBingApi(place):
    coordinate = None
    bbox = None
    position = geocoder.bing(place, key=BING_KEY) 
    if position.json:
        #get coordinate of the place
        coordinate = (position.json['lat'], position.json['lng'])
        
        #get the coordinates of the bbox
        lat_min = position.json['bbox']['southwest'][0]
        lat_max = position.json['bbox']['northeast'][0]
        lon_min = position.json['bbox']['southwest'][1]
        lon_max = position.json['bbox']['northeast'][1]     
        bbox = ((lat_min, lat_max), (lon_min, lon_max))
    
    return coordinate, bbox
    

"""
This method receives as input a list of places and returns the representative coordinate for the tweet 
with those places.
"""
def getCoordFromPlace(tweet, places, heuristic):
    coordinate = None
            
    if heuristic == Heuristic.third:
        if places:
            place = " ".join(places)
            coordinate, _ = sendRequestBingApi(place)
    else:
        #form of elem in list <(lat_min,lat_max), (lon_min, lon_max)>.
        coord_bbox = []
        
        #form of elem in list <lat, lon>
        coord_couples = []
        for place in places:
            lat_lon, bbox = sendRequestBingApi(place)
            
            #It occurs if the place has geographic coordinates. The check on the bbox is useless as the first 
            #condition is sufficient to guarantee its existence for that place
            if lat_lon is not None:
                coord_bbox.append(bbox)
                coord_couples.append(lat_lon)
            
        if len(coord_couples) > 1:
            candidate_places, coord_couples = prefilteringCoordinates(places, coord_couples, coord_bbox)
        
            #If there are coordinates for more than one place, 
            #a heuristic is performed that allows you to keep coordinates of only one place
            if len(coord_couples) > 1:
                #Selection of the first place detected in coord_couples, 
                #as well as the first place detected in the tweet
                if heuristic == Heuristic.first:
                    coordinate = coord_couples[0]
                     
                #Concatenation of candidate places with subsequent new research
                elif heuristic == Heuristic.second:
                    place = " ".join(candidate_places)
                    coordinate, _ = sendRequestBingApi(place)
            elif len(coord_couples) == 1:
                coordinate = coord_couples[0]
                
        elif len(coord_couples) == 1:
            coordinate = coord_couples[0]
    
    #If coordinates is still None, then the hastags of the current tweet are examined to find one 
    #that represents a place
    if coordinate is None:
        hastags = getHastags(tweet)
        for i in range(0, len(hastags)):
            place = hastags[i].replace("#", "")
            coordinate, _ = sendRequestBingApi(place)
            if coordinate is not None:
                break
              
    return coordinate
    

"""
This method removes duplicates from the input list
"""
def removeDuplicate(elements_list):
    res = []
    for elem in elements_list:
        if elem not in res:
            res.append(elem)
    return res


def getNE(tweet, filters):
    new_doc = nlp(tweet)
        
    entities = []
    for ent in new_doc.ents:
        text = ent.text
        if "https" not in text:
            if ent.label_ not in filters:
                entities.append(ent.text)
    return entities


def read_tsv(tsv):
    df = pd.read_csv("predictions/" + tsv, delimiter = "\t", encoding='cp1252', names = ["Tweet", "Sentiment"])
    return df


"""
This method write triples <tweet, sentiment, coordinate> in tsv file specified in the arguments
"""
def dataFrameToTsv(dataset, tsv_file):
    df = pd.DataFrame(dataset, columns = ["Tweet", "Sentiment", "Coordinate"]) 
    df.to_csv(tsv_file, sep = "\t", index = False, line_terminator='\n')


def remove_emoji(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U00002500-\U00002BEF"  # chinese char
                           u"\U00002702-\U000027B0"
                           u"\U0001f926-\U0001f937"
                           u"\U00010000-\U0010ffff"
                           u"\u2640-\u2642" 
                           u"\u2600-\u2B55"
                           u"\u200d"
                           u"\u23cf"
                           u"\u23e9"
                           u"\u231a"
                           u"\ufe0f"  # dingbats
                           u"\u3030"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def cleaning_stopwords(tweet):
    #return " ".join([word for word in str(text).split() if word not in stop_words])
    
    tweet_nlp = nlp(tweet)
    # Create list of word tokens after removing stopwords
    filtered_sentence =[] 
    
    token_list = []
    for token in tweet_nlp:
        token_list.append(token.text)
    
    for word in token_list:
        lexeme = nlp.vocab[word]
        if lexeme.is_stop == False:
            filtered_sentence.append(word) 
    return " ".join(filtered_sentence) 


english_punctuations = string.punctuation
punctuations_list = english_punctuations
def cleaning_punctuations(text):
    translator = str.maketrans('', '', punctuations_list)
    return text.translate(translator)


def cleaning_repeating_char(text):
    return re.sub(r'(.)1+', r'1', text)


def cleaning_URLs(text):
    pattern_re = "https?:\S+|http?:\S|[^A-Za-z0-9]+"
    return re.sub(pattern_re, ' ', text)


def cleaning_tags(text):
    pattern_re = "@\S+|RT @\S+"
    return re.sub(pattern_re, ' ', text)  


def cleaning_URLs_and_tagging(text):
    text = cleaning_URLs(text)
    return cleaning_tags(text)


def cleaning_numbers(text):
    return re.sub('[0-9]+', '', text)


st = nltk.PorterStemmer()
def stemming_on_text(tokens):
    text = [st.stem(word) for word in tokens]
    return text

lm = nltk.WordNetLemmatizer()
def lemmatizer_on_text(tokens):
    text = [lm.lemmatize(word) for word in tokens]
    return text


def cleaning_tweet(tweet):
    #print(tweet)
    tweet = cleaning_URLs_and_tagging(tweet)
    tweet = cleaning_stopwords(tweet)
    tweet = cleaning_punctuations(tweet)
    tweet = cleaning_repeating_char(tweet)
    tweet = cleaning_numbers(tweet)
    
    #tokenization is used for stemming and lemmatization
    tokenized_tweets = word_tokenize(tweet)
    tweet = stemming_on_text(tokenized_tweets)
    
    #print(tweet)
    #print("*********************************************")
    return lemmatizer_on_text(tweet)


"""
With this method, tweets are cleared of stopwords, punctuation, URLs, repeated characters, numbers. 
Stemming and lemmatization are also applied to tweets. This method is used for sentiment analysis
Method return DataSeries of cleaned tweets
"""
def preprocessing(tweets):
    cleaned_tweets = [cleaning_tweet(tweet) for tweet in tweets]
    return pd.Series(cleaned_tweets)


"""
With this method, tweet are cleared of stopwords, numbers, tags. 
Stemming and lemmatization are also applied to tweets. This method is used for sentiment analysis
Method return DataSeries of cleaned tweets
"""
def cleaningForNE(tweet):
    tweet = cleaning_tags(tweet)
    tweet = tweet.replace("’s", '')
    tweet = cleaning_stopwords(tweet)
    tweet = tweet.replace("...", "")
    tweet = tweet.replace("â", "")
    tweet = tweet.replace("#", "")
    return cleaning_numbers(tweet)