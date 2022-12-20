import pandas as pd
import os
import numpy as np
from PIL import Image, ImageOps
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# replace multi-word expressions with hyphens or single word synonms
multi_words = ['event related potential', 'event related', 'evoked potential',
               'related potential', 'machine learning', 'long term memory',
               'attentional', 'attention deficit']

replacement_text = ['ERP', 'ERP', 'evoked_potential', 'ERP', 'machine_learning', 'long_term_memory', 'attention', 'ADHD']

# additional terms not needed
ignore_words = ['eeg', 'electroencephalography', 'electroencephalogram', 'neural', 'electrical', 'brain', 'neuronal',
                'electroencephalographic', '‘', 'mri', 'data', 'meg', 'eeg/meg', "'s", 'task', 'human',
                'using', 'influence', 'correlate', 'stimulus', 'different', 'difference', 'investigation',
                'modulate', 'study', 'evidence', 'child', 'modulation', 'effect', 'analysis', 'development',
                'system', 'change', 'dynamic', 'function', 'norm', 'gender', 'gene', 'test',
                'electrophysiology', 'electrophysiological', 'cognitive', 'adult', 'performance',
                'event', 'related', 'potential', 'fmri', 'behavioral', 'eye', 'activity', 'evaluation',
                'status', 'associated', 'neurophysiological', 'response', 'signal', 'early', 'association',
                'individual', 'evaluation', 'mechanism', 'age', 'level', 'relationship', 'role', 'process',
                'activation', 'comparison', 'reveal', 'index', 'mechanism', 'outcome', 'treatment',
                'application', 'increased', 'dependent', 'enhanced', 'subject', 'reflect', 'experience',
                'revealed', 'patient', 'based', 'correlation', 'increased', 'measure', 'quantitative', 'increase',
                'combined', 'integration', 'versus', 'new', 'distinct', 'young', 'processing', 'cortical',
                'altered', 'pilot', 'non', 'biomarker', 'marker', 'improve', 'infant', 'older', 'method',
                'differential', 'recording', 'information', 'characteristic', 'two', 'area', 'reveals',
                'assessment', 'finding', 'specific', 'approach', 'within', 'toward', 'reduce', 'reduced'
                'modulates', 'adolescent', 'across', 'following', 'paradigm', 'insight', 'interaction',
                'variability', 'neuron', 'without', 'identification', 'multiple', 'use', 'novel', 'signature',
                'neuropsychological', 'diagnosis', 'simultaneous', 'acute', 'word', 'adaptation', 'type', 'profile',
                'sex', 'normal', 'alter', 'term', 'tm', 'v', 'pre', 'timing', 'contribution', 'scalp', 'among',
                'behavior', 'electrocortical', 'source', 'video', 'short', 'physiological', 'syndrome', 'region',
                'tracking', 'alteration', 'behavioural', 'structure', 'impact', 'case', 'imaging', 'like',
                'cognition', 'underlying', 'cerebral', 'cortex', 'image', 'de', 'self', 'duration', 'subjective',
                'reflect', 'parameter', 'preliminary', 'show', 'hz', 'pre', 'report']


def preprocess_titles(df):
    # Extract titles
    study_titles = df['Title'].to_list()
    study_years = df['Year'].to_list()

    stop_words = set(stopwords.words('english'))
    wordnet_lemmatizer = WordNetLemmatizer()

    titles_hyphened = []
    for title in study_titles:
        for i, multi_word in enumerate(multi_words):
            if multi_word in title:
                title = title.replace(multi_word, replacement_text[i])
                break
        titles_hyphened.append(title)


    # tokenize
    tokenized_titles = [word_tokenize(title.lower()) for title in titles_hyphened]

    allClean_titles = []
    for title in tokenized_titles:
        title_filtered = []
        for token in title:
            # filter stop words, punctuation, and general terms
            if token not in stop_words and token not in string.punctuation:

                # lemmatize token
                token_lemm = wordnet_lemmatizer.lemmatize(token)

                if token_lemm not in ignore_words:

                    title_filtered.append(token_lemm)

        allClean_titles.append(title_filtered)

    return allClean_titles


if __name__ == '__main__':

    dataDir = r'.\proquest_searches\word_cloud'

    files = os.listdir(dataDir)

    # Merge Data
    allYears_df = pd.DataFrame()
    for file in files:
        year = int(file[:file.index('_scrape')])
        df = pd.read_csv(os.path.join(dataDir, file))

        # add column for year incase want to do word cloud by year
        df['Year'] = year

        allYears_df = pd.concat([allYears_df, df], ignore_index=True)

    all_processedTitles = preprocess_titles(allYears_df)

    # Word Cloud requires a single string
    wordcloud_string = [' '.join(title) for title in all_processedTitles]

    #vec = TfidfVectorizer(ngram_range=(1, 2))
    #vec = vec.fit(wordcloud_string)

    #foo = pd.DataFrame({'Term': vec.get_feature_names_out(), 'TDIF': vec.idf_})

    wordcloud_string = ' '.join(wordcloud_string)

    word_cloud = WordCloud(width=3000, height=2000,
                           random_state=1, background_color='white',
                           collocations=True, stopwords=set(ignore_words),
                           max_words=300, collocation_threshold=30).generate(wordcloud_string)

    word_cloud.to_file('allTitles_wordCloud.jpg')

    plt.figure(figsize=(8, 8), dpi=80)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()
