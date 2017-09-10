import json

import itertools
import pymongo


if __name__ == '__main__':
    documents = pymongo.MongoClient().ir.abstracts
    inverted_index = dict() #Match stemmed word to list of doc_ids
    for document in documents.find({"raw_tokens":{"$exists":True},"text":{"$exists":True}}):
        for word in itertools.chain(document["text"],document["raw_tokens"]):
            if word in inverted_index.keys():
                inverted_index[word].append(document["Award Number"])
            else:
                document_ids_list = list()
                document_ids_list.append(document["Award Number"])
                inverted_index[word] = document_ids_list

    with open('inverted_index.json', 'w') as fp:
        json.dump(inverted_index, fp)