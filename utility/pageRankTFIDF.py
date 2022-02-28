import pandas as pd
import pickle
import numpy as np
from scipy.spatial import distance
from utility.utils import *

from nltk.corpus import stopwords
stop_words = stopwords.words('english')


def get_symmetric_matrix(matrix):
    """
    Get Symmetric matrix
    :param matrix:
    :return: matrix
    """
    return matrix + matrix.T - np.diag(matrix.diagonal())



class TextRankTweet():
    def __init__(self):
        self.damping = 0.85  # damping coefficient, usually is .85
        self.min_diff = 1e-5  # convergence threshold
        self.steps = 100  # iteration steps
        self.text_str = None
        self.sentences = None
        self.pr_vector = None

    def _sentence_similarity(self, sent1, sent2, stopwords=None):
        cosine_similarity = 1 - distance.cosine(sent1, sent2)
        return cosine_similarity
    
    def _build_similarity_matrix(self, sentences):
        size = sentences.shape[0]
        # create an empty similarity matrix
        sm = np.zeros([size, size])

        for idx1 in range(size):
            for idx2 in range(size):
                if idx1 == idx2:
                    continue
                
                similarity = self._sentence_similarity(sentences[idx1], sentences[idx2])
                sm[idx1][idx2] = similarity                  
        # Get Symmeric matrix
        sm = get_symmetric_matrix(sm)

        # Normalize matrix by column
        norm = np.sum(sm, axis=0)
        sm_norm = np.divide(sm, norm, where=norm != 0)  # this is ignore the 0 element in norm

        return sm_norm


    def _run_page_rank(self, similarity_matrix):
        pr_vector = np.array([1] * len(similarity_matrix))

        # Iteration
        previous_pr = 0
        for epoch in range(self.steps):
            pr_vector = (1 - self.damping) + self.damping * np.matmul(similarity_matrix, pr_vector)
            if abs(previous_pr - sum(pr_vector)) < self.min_diff:
                break
            else:
                previous_pr = sum(pr_vector)
        return pr_vector


    def _get_sentence(self, index):

        try:
            return self.sentences[index]
        except IndexError:
            return ""

    def get_top_sentences(self, number=1):
        top_sentences = []

        if self.pr_vector is not None:
            sorted_pr = np.argsort(self.pr_vector)
            sorted_pr = list(sorted_pr)
            sorted_pr.reverse()

            index = 0
            for epoch in range(number):
                sent = self.sentences[sorted_pr[0]]
                #score = self.pr_vector[sorted_pr[index]]
                #top_sentences.append([sent,score])
                top_sentences.append(sent)
                index += 1

        return top_sentences


    def analyze(self, tweets, embedding_vecs, stopwords=None):
        self.sentences = tweets
        similarity_matrix = self._build_similarity_matrix(embedding_vecs)
        self.pr_vector = self._run_page_rank(similarity_matrix)
        

        
def computeTextRank(tweets, embedding_model_filename):
    cleaned_tweets = preprocessing(tweets)

    #embeddings
    vectoriser = pickle.load(open(embedding_model_filename, 'rb'))
    embeddings = vectoriser.transform(cleaned_tweets.apply(lambda x: " ".join(x)))

    text_rank = TextRankTweet()
    text_rank.analyze(tweets, embeddings.toarray())

    return text_rank.get_top_sentences()