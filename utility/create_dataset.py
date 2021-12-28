# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 10:33:42 2021

@author: Utente
"""

import xml.etree.ElementTree as ET
import re


def creation_sentences_dataset(tweets_xml, mode):
    tree = ET.parse(tweets_xml)
    root = tree.getroot()

    dataset = open("../dataset/tweets_dataset.txt", mode, encoding="utf-8")
    
    #file in cui sono riportati i riferimenti(indici di posizione) ai tweet no-sop 
    #file_indexes_nsop = open("index_nsop.txt", "w", encoding="utf-8")
    
    #indexes_no_sop = []
    for i, elem in enumerate(root):
        if elem[1].text == "Y":
            #sentence = elem[0].text.replace("#", " ")
            #sentence = remove_emoji(sentence)
            #dataset.write(sentence + "\n")
            dataset.write(elem[0].text + "\n")
        #else:
            #indexes_no_sop.append(i)
    
    """for element in indexes_no_sop:
        file_indexes_nsop.write(str(element) + "\n")"""


    #file_indexes_nsop.close()
    dataset.close()
        

creation_sentences_dataset('../dataset/sop_dataset.xml', "w")
creation_sentences_dataset('../dataset/london.xml', "a")