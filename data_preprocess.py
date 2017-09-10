import string

import nltk
import pymongo
from nltk import SnowballStemmer, tokenize


if __name__ == '__main__':
    # Database
    documents = pymongo.MongoClient().ir.abstracts

    nltk.download('punkt')

    stemmer = SnowballStemmer("english")

    for document in documents.find({"raw_tokens":{"$exists":False},"text":{"$exists":True}}): #Process only unprocessed documents
        # text = document["Title"] + ". " + document["Abstract"]
        # tokens = tokenize.word_tokenize(text.translate(str.maketrans("","", string.punctuation))) #tokenize string without punctuation
        # stems = [stemmer.stem(token) for token in tokens]
        # document["text"]=stems
        raw_tokens_text = [value for key, value in document.items() if key not in {"Title","Abstract","_id","File","Total Amt","text"}]
        raw_tokens_text = " ".join(x for x in raw_tokens_text).translate(str.maketrans("","", string.punctuation))
        document["raw_tokens"] = tokenize.word_tokenize(raw_tokens_text)
        documents.find_one_and_replace({"Award Number":document["Award Number"]},document)
