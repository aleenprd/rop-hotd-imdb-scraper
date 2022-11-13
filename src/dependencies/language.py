
from general import flatten

def get_n_grams(df: pd.DataFrame):
    corpus = (" ").join(df["full_review_text_clean"])
    unigrams = corpus.split()
    bigrams, trigrams = (ngrams(unigrams, x) for x in (2,3))
    unigrams_freq, bigrams_freq, trigrams_freq = (
        collections.Counter(x) for x in (unigrams, bigrams, trigrams)
    )
    return unigrams_freq, bigrams_freq, trigrams_freq

def search_gram():
    pass 


def get_names_entities(corpus: str, desirable_entities: List[str]=['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'EVENT', 'WORK_OF_ART', 'LANGUAGE', 'MONEY']):
    doc = nlp(corpus)
    corpus_entities = [tuple([X.text, X.label_]) for X in doc.ents if X.label_ in desirable_entities]
    return corpus_entities


def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]
