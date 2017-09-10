import search_engine as se

if __name__ == '__main__':
    print("Loading search engine")
    engine = se.SearchEngine()
    print("Please input your query: ")
    query = input()

    try:
        print("Please enter number of results to be shown: ")
        number_of_results = int(input())
    except ValueError:
        print("That's not an int! Setting value to 10")
        number_of_results = 10

    # Test whether query is logical or not
    if " AND " in query or "NOT " in query or " OR " in query:
        search_results, number_of_entries = engine.search_boolean(query, number_of_results,True)
    else:
        search_results, number_of_entries = engine.search_simple(query, number_of_results,True)

    print("Found {} entries".format(number_of_entries))
    print(search_results)
