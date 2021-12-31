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
#from nltk.corpus import stopwords

#stop_words = set(stopwords.words('english'))
nlp = spacy.load("en_core_web_sm")

BING_KEY = "AjttQre1RsLFdGceLZYGGUWx0f3NY3ZyJiUU7tbTtWalvxVhSXhGH1kd1mMh0KzB"


"""
This method removes the coordinates of places contained in other places. 
The method returns the list of filtered places and their respective coordinates.

Example: San Francisco is contained in California
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


"""
This method receives as input a list of places and returns the representative coordinate for the tweet 
with those places
"""
def getCoordFromPlace(places):
    #form of elem in list <lat, lon>
    coord_couples = []
    
    #form of elem in list <(lat_min,lat_max), (lon_min, lon_max)>.
    coord_bbox = []
    for place in places:
        position = geocoder.bing(place, key=BING_KEY)
        
        #get the coordinates of the bbox
        lat_min = position.json['bbox']['southwest'][0]
        lat_max = position.json['bbox']['northeast'][0]
        lon_min = position.json['bbox']['southwest'][1]
        lon_max = position.json['bbox']['northeast'][1]
        
        bbox = ((lat_min, lat_max), (lon_min, lon_max))
        coord_bbox.append(bbox)
        
        #get coordinate of the place
        lat_lon = (position.json['lat'], position.json['lng'])
        coord_couples.append(lat_lon)
        
    candidate_places, coord_couples = prefilteringCoordinates(places, coord_couples, coord_bbox)
    
    if len(candidate_places) > 1:
        #TO DO
        1)concatenare i luoghi e computare le coordinate
        2)sfruttare i types dei luoghi
        3)selezione del primo luogo rilevato
    

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
    tweet = tweet.replace("'s", '')
    tweet = cleaning_stopwords(tweet)
    tweet = tweet.replace("...", "")
    tweet = tweet.replace("â", "")
    return cleaning_numbers(tweet)