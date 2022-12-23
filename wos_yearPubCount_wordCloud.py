import pandas as pd
import os
import matplotlib.pyplot as plt

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud
from nltk.corpus import stopwords

if __name__ == '__main__':

    dataDir = r'.\wos-searches'
    files = os.listdir(dataDir)

    # column names can be found here https://images.webofknowledge.com/images/help/WOS/hs_wos_fieldtags.html
    # PY is publication year, DE is keywords, TI is title, AB is abstract
    columns_oi = ['TI', 'AB', 'DE', 'PY']

    topics = ['ERP', 'MOBILE', 'TF', 'PC']

    # Merge Files
    all_searchesDf = pd.DataFrame()
    for file in files:
        # get topic
        file_topic = [topic for topic in topics if topic in file]

        searchDf = pd.read_csv(os.path.join(dataDir, file), sep="\t")

        searchDf = searchDf[columns_oi]

        searchDf['Topic'] = file_topic[0]

        all_searchesDf = pd.concat([all_searchesDf, searchDf], ignore_index=True)

    new_columnNames = ['Title', 'Abstract', 'Keywords', 'Year', 'Topic']
    all_searchesDf = all_searchesDf.rename(columns=dict(zip(columns_oi + ['Topic'], new_columnNames)))

    # select years between 2000-2021
    all_searchesDf = all_searchesDf[(all_searchesDf['Year'] > 1999) & (all_searchesDf['Year'] < 2022)]

    all_searchesDf['Year'] = all_searchesDf['Year'].astype('int')

    # group publications by year
    year_pubCounts = all_searchesDf.groupby(['Year', 'Topic']).Title.count()

    plot_pubcounts=False
    if plot_pubcounts:
        # plot Pubs by year
        fig, ax = plt.subplots(figsize=(10, 5), dpi=80)
        year_pubCounts.unstack().plot.bar(ax=ax, alpha=0.7, stacked=True,
                                          rot=45, fontsize=12)
        ax.set_ylabel('Count')
        ax.set_title('Publication Count by Year')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(labels=['ERP', 'Mobile', 'Time Frequency', 'Decoding'], frameon=False)

        plt.savefig('wos_yearPubCount.jpg', bbox_inches='tight')

        plt.show()

        plt.close(fig)

    # plot WordCloud
    keywords = all_searchesDf['Keywords'].to_list()

    split_keywords = [str(words).split('; ') for words in keywords]

    # flatten list
    keyword_flatList = [word.strip().lower() for sublist in split_keywords for word in sublist]

    stop_words = stopwords.words('english')
    ignore_words = ['eeg', 'electroencephalography', 'electroencephalogram', 'neural', 'electrical', 'brain',
                    'neuronal', 'electroencephalographic', '‘', 'mri', 'data', 'meg', 'eeg/meg', 'task', 'human',
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
                    'reflect', 'parameter', 'preliminary', 'show', 'hz', 'pre', 'report', 'magnetic stimulation',
                    'ERP ERP', 'detection', 'bci bci', 'model', 'transcranial magnetic', 'differences',
                    'magnetic resonance']

    no_stops = [word for word in keyword_flatList if word not in ignore_words + stop_words]

    word_net = WordNetLemmatizer()

    lem_words = [word_net.lemmatize(word) for word in no_stops]

    # replace synonms
    synonms = ['event related potential', 'event related', 'related potential', 'evoked potential',
               'long term memory', 'brain computer interface', 'brain-computer interface', 'bci',
               'attentional', 'attention deficit',
               'convolutional neural network', 'support vector machine', 'working memory',
               'machine learning', 'deep learning']

    replacements = ['ERP', 'ERP', 'ERP', 'evoked-potential',
                    'long_term_memory', 'bci', 'bci', 'bci',
                    'attention', 'ADHD',
                    'CNN', 'svm', 'working_memory',
                    'machine-learning', 'deep-learning']

    clean_words = []
    synonm_check = False
    for word in lem_words:

        # check if word is one of the synonms
        if word in synonms:
            synonm_check = True
            synonm_idx = synonms.index(word)
            clean_words.append(replacements[synonm_idx])

        else:
            # check if synonm is a substring
            for i, synonm in enumerate(synonms):
                if synonm in word:
                    synonm_check = True
                    clean_words.append(replacements[i])

        if not synonm_check:
            clean_words.append(word)

        synonm_check = False

    wordcloud_string = ' '.join(clean_words)

    word_cloud = WordCloud(width=3000, height=2000,
                           random_state=1, background_color='white',
                           collocations=True, stopwords=set(ignore_words + stop_words + ['nan']),
                           max_words=200, collocation_threshold=10).generate(wordcloud_string)

    word_cloud.to_file('wos_allTitles_wordCloud.jpg')

    plt.figure(figsize=(8, 8), dpi=80)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

