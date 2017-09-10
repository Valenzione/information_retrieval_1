import json

from nltk import SnowballStemmer, word_tokenize
from pymongo import MongoClient

from lepl import Optional, String, Word, Delayed, Drop, DroppedSpace


class SearchEngine():
    def __init__(self):
        self.documents = MongoClient().ir.abstracts
        self.stemmer = SnowballStemmer("english")
        self.all_documents = set(line.strip() for line in open('list_of_ids'))
        with open('inverted_index.json') as data_file:
            self.inverted_index = json.load(data_file)

    def search_boolean(self, query, number_of_results=10,only_ids=False):

        def parse_query( query_input):

            def ander(result):
                if len(result) == 2:
                    return (result[0], result[1])
                return result[0]

            def parse_not(term):
                if isinstance(term, tuple):
                    return (parse_not(term[0]), parse_not(term[1]))  # return tuple parsed for NOT from both sides
                else:
                    if term.startswith("NOT "):
                        return ("NOT", term[4:])
                    else:
                        return (term)

            text = Optional("NOT ") + (String() | Word())
            andAfter = Delayed()
            with DroppedSpace():
                andClause = (text) & andAfter > ander
                andAfter += (Drop('AND') & (andClause | text) & (andAfter))[:]
                expr = andClause | text
                query = expr & (Drop('OR') & expr)[:]
                parsed_query = query.parse(query_input)
                parsed_query = [parse_not(term) for term in parsed_query]
                return parsed_query

        def generate_post_lists( parsed_query):

            def get_phrase_post_list(phrase):
                tokens = [self.stemmer.stem(x) for x in word_tokenize(phrase)]  # contains all stems
                posts = list()
                for token in tokens:

                    if token in self.inverted_index.keys():
                        doc_ids = set(self.inverted_index[token])
                    else:
                        doc_ids = set()
                    posts.append(doc_ids)
                posts = set.intersection(*posts)
                return posts

            # Parse each term recursively and return set of post id's
            def parse_term(term):

                if isinstance(term, tuple):
                    if (term[0] == "NOT"):
                        return self.all_documents.difference(parse_term(term[1]))
                    else:
                        return parse_term(term[0]).intersection(parse_term(term[1]))
                else:
                    return get_phrase_post_list(term)

            post_list = set()
            for term in parsed_query:
                ids = parse_term(term)
                post_list = post_list.union(ids)

            return post_list

        def rank_tf_idf( posts, query_tokens):
            doc_dict = dict()
            query_tokens = [self.stemmer.stem(x) for x in query_tokens]  # contains all stems

            # Create dictionary with tokens as keys and values as dictionaries with documents as keys and tf-idf as valu
            for token in query_tokens:
                tf = dict()
                if token in self.inverted_index.keys():
                    idf = len(self.inverted_index[token])
                    for doc_id in self.inverted_index[token]:
                        if doc_id in tf.keys():
                            tf[doc_id] += 1
                        else:
                            tf[doc_id] = 1

                    for key, value in tf.items():
                        tf[key] = value / idf
                doc_dict[token] = tf

            # Return empty list with no results
            if len(doc_dict)==0 or len(posts) == 0:
                return list()

            # Aggregate multiple tf_idf values for different tokens into one dictionary
            aggregated_dict = dict()
            for item in doc_dict:
                for key, value in doc_dict[item].items():
                    if key in aggregated_dict.keys():
                        aggregated_dict[key] += value
                        aggregated_dict[key] *= 2
                    else:
                        aggregated_dict[key] = value

            # maps tf_idf calculated value to found results. Set 0 if no tf-idf was calculated tf idf is 0 usually for
            # results found with NOT query
            tf_idf = {id: aggregated_dict[id] if id in aggregated_dict.keys() else 0 for id in posts}
            # sort tf-idf dict over tf_idf value
            sorted_tf_idf = [k for k in sorted(tf_idf, key=tf_idf.get, reverse=True)]

            return sorted_tf_idf


        # Parse query, find all posts, then rank them with tf-idf.
        parsed_query = parse_query(query)
        query_tokens = [x for x in word_tokenize(query) if x not in {"AND", "NOT", "OR"}]
        posts = generate_post_lists(parsed_query)
        posts = rank_tf_idf(posts, query_tokens)

        if only_ids:
            return  posts[:number_of_results], len(posts)

        result_list = list()
        for doc_id in posts[:number_of_results]:
            result_list.append(self.documents.find_one({"Award Number": doc_id}))
        return result_list, len(posts)

    def search_simple(self, query, number_of_results=10,only_ids = False):
        global tf

        result_list = list()  # List with final results
        tf_idf = dict()  # TF-IDF dictionary matching doc_id to occurences of stemmed token in this doc_id

        stemmed_tokens = [self.stemmer.stem(x) for x in word_tokenize(query)]

        for token in stemmed_tokens:
            tf = None
            if token in self.inverted_index.keys():
                idf = len(self.inverted_index[token])
                tf = dict()
                for doc_id in self.inverted_index[token]:
                    if doc_id in tf.keys():
                        tf[doc_id] += 1
                    else:
                        tf[doc_id] = 1

                for key, value in tf.items():
                    tf[key] = value / idf
            tf_idf[token] = tf

        if tf is None:
            return list()

        aggregated_dict = dict()  # Aggregate multiple stems dictionaries to sinle document list
        for item in tf_idf:
            for key, value in tf_idf[item].items():
                if key in aggregated_dict.keys():
                    aggregated_dict[key] += value
                    aggregated_dict[key] *= 2
                else:
                    aggregated_dict[key] = value

        ranked_tf_idf_results = [(k, aggregated_dict[k]) for k in sorted(aggregated_dict, key=aggregated_dict.get, reverse=True)]

        if only_ids:
            return  ranked_tf_idf_results[:number_of_results], len(ranked_tf_idf_results)

        for doc_id, value in ranked_tf_idf_results[:number_of_results]:
            result_list.append(self.documents.find_one({"Award Number": doc_id}))

        return result_list, len(ranked_tf_idf_results)
