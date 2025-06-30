import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from thefuzz import fuzz    
from django.db import connection
import string
import sqlite3

class Search(): # By having 2 different search functions, I am able to have a list of different returns decreasing in relevancy
    # Additionally, they both complement eachother to ensure that no items are missed

    def __init__(self, query, category):
        self.query=query
        self.category=category

    def prompt_clean(self, search_prompt):

        # This function basically cleans the search prompt and reduces it to its core

        tokens = word_tokenize(search_prompt)
        
        # Remove punctuation and stop words
        tokens = [word for word in tokens if word not in string.punctuation]
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]

        stemmer = PorterStemmer()
        stemmed_tokens = [stemmer.stem(word) for word in tokens]
        tagged_tokens=nltk.pos_tag(stemmed_tokens)
        cleaned_tokens = []

        # This ensures only certain parts of query are searched for
        for x in range(len(stemmed_tokens)):
            accepted_tags = ["CD", "NN", "NNS", "NNP", "NNPS", "JJ", "JJR", "JJS"]

            if tagged_tokens[x][1] in accepted_tags:
                cleaned_tokens.append(tagged_tokens[x][0].lower())
        return cleaned_tokens
    
    def keyword_search(self):
        # This is the keyword search function that searches based on keywords and their stems

        # Cleaning the search prompt to simplify it and reduce it to its core
        cleaned_tokens=self.prompt_clean(self.query)
        results=[]
#
        if len(self.category) == 1:
            tuple_category = (self.category[0],'')
        else:
            tuple_category = tuple(self.category)

        with connection.cursor() as sql:
            sql.execute(f"SELECT item_name FROM Parts WHERE category IN {tuple_category}")
            item_names=sql.fetchall()

        for i in range(len(item_names)):

            # Cleans the item names by the same function as the search prompt to ensure they would reduce to the same thing
            current_item_token=self.prompt_clean(item_names[i][0])

            # Looks through all of the cleaned parts of the search prompt and checks if they match parts of the item name
            for x in range(len(cleaned_tokens)):

                if cleaned_tokens[x] in current_item_token:
                    with connection.cursor() as sql:
                        sql.execute(f"SELECT * FROM Parts WHERE item_name = '{item_names[i][0]}'")
                        returned=sql.fetchall()

                    if returned:
                        
                        results.append([returned[0]])
        return results

    def fuzzy_search(self): # stem the search query and item name to decrease lookup time and maybe remove a loop
        # Also maybe make it so it disrehgards parts already found
        self.search_prompt = self.query.split()

        results=[]

        if len(self.category) == 1:
            tuple_category = (self.category[0],'')
        else:
            tuple_category = tuple(self.category)

        with connection.cursor() as sql:
            sql.execute(f"SELECT item_name FROM Parts WHERE category IN {tuple_category}")
            item_names=sql.fetchall() # Gets all the relevant items to compare against 
            sql.execute(f"SELECT merchant_name FROM Parts WHERE category IN {tuple_category}")
            merchant_names=sql.fetchall() # Gets all the relevant merchants to compare against

        merchant_item_names=[] # This is where all the items and their merchants will be stored

        for x in range(len(item_names)):
            item_list=item_names[x][0].split()
            item_list.append(merchant_names[x][0]) # Appends the merchant name to the end of the item name
            merchant_item_names.append(item_list) 

        item_ratios=[] # This is where all of the ratios and their items will be stored

        for i in range(len(merchant_item_names)):
            for x in range(len(self.search_prompt)):

                current_item_token=merchant_item_names[i]

                for j in range(len(current_item_token)):

                    # Essentially compares all the words of the search prompt with all the words of every return 

                    simple_ratio=fuzz.ratio(self.search_prompt[x], current_item_token[j])
                    token_ratio=fuzz.token_sort_ratio(self.search_prompt[x], current_item_token[j])

                    largest_current_ratio=max(simple_ratio, token_ratio) # Gets the largest ratio from the 2 different methods
                    item_ratios.append([largest_current_ratio, merchant_item_names[i][-1]])

        # Sorts the ratios in ascending order, specifying to sort by the ratio value
        sorted_ratios=sorted(item_ratios, key=lambda x:x[0], reverse=True)
        results=[]

        for x in range(len(sorted_ratios)): 

            if sorted_ratios[x][0] >= 60: # 60 is the limit where most unneccesary searches will be filtered out
                with connection.cursor() as sql:
                    sql.execute(f"""SELECT * FROM Parts WHERE merchant_name = '{sorted_ratios[x][1]}' 
                                AND category IN {tuple_category}""")
                    returns=sql.fetchall()
                if returns:
                    results.append([returns[0]])


        return results

