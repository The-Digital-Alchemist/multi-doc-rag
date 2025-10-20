import spacy
from typing import List, Iterable
from spacy.lang.en.stop_words import STOP_WORDS

# Load the spaCy model once; exclude heavy components for speed
nlp = spacy.load("en_core_web_sm")

# Preserve negations; filter other stopwords
NEGATIONS = {"no", "not", "never"}
CUSTOM_STOPWORDS = {w for w in STOP_WORDS if w not in NEGATIONS}


def preprocess_doc(doc) -> List[str]:
    """
    Preprocess a spaCy document into normalized tokens for BM25 indexing.
    
    This internal function applies consistent tokenization rules including
    lemmatization, stopword removal (preserving negations), and filtering
    of punctuation and short tokens.
    
    Args:
        doc: spaCy processed document object
        
    Returns:
        List[str]: List of normalized tokens ready for BM25 indexing
    """
    tokens: List[str] = []
    for token in doc:
        if token.is_space or token.is_punct:
            continue
        term = (token.lemma_ or token.text).lower()
        if (term in CUSTOM_STOPWORDS) and (term not in NEGATIONS):
            continue
        if not token.like_num and len(term) < 2:
            continue
        tokens.append(term)
    return tokens


def preprocess_text(text: str) -> List[str]:
    """
    Preprocess a single text string into BM25-ready tokens.
    
    This function applies consistent text normalization including lemmatization,
    stopword removal (while preserving negations), and filtering of punctuation
    and short tokens. The same preprocessing rules are applied during both
    indexing and querying to ensure consistent lexical search results.
    
    Args:
        text (str): Input text to preprocess
        
    Returns:
        List[str]: List of normalized tokens suitable for BM25 search
        
    Example:
        >>> text = "Running is not supported in versions 3.1-3.2"
        >>> tokens = preprocess_text(text)
        >>> print(tokens)  # ['run', 'not', 'support', 'version', '3.1', '3.2']
    """
    doc = nlp(text)
    return preprocess_doc(doc)


def batch_preprocess_texts(texts: Iterable[str]) -> List[List[str]]:
    """
    Preprocess multiple text strings efficiently using spaCy's batch processing.
    
    This function processes multiple texts in batches for improved performance
    during document indexing operations. It applies the same normalization
    rules as preprocess_text but handles multiple inputs efficiently.
    
    Args:
        texts (Iterable[str]): Iterable of text strings to preprocess
        
    Returns:
        List[List[str]]: List of token lists, one for each input text
    """
    results: List[List[str]] = []
    for doc in nlp.pipe(texts, batch_size=64):
        results.append(preprocess_doc(doc))
    return results