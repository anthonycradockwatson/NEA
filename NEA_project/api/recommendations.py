from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from django.db import connection
import math
import numpy as np
from .cosine_similarity import cos_similarity
from .mergesort import return_sorted_list

# try add a collaborative filter where it considers users wth the siimilar cars 

def recommendation(models, user_id, category):

    # This function takes in a list of part objects and returns a list of recommended parts based on the users liked items
    # It uses a combination of cosine similarity and weighted ratings to determine the best parts to recommend

    parts=[]
    sorted_models=[]
    for i in range(len(models)):
        parts.append(vars(models[i]))
    liked_item_ratings=[]

    if user_id is not None and user_id != "":  # Check if user_id is provided to allow for anonymous users 

        liked_item_ratings=liked_item_comparison(parts, user_id)

    weighted_ratings=weighting(parts, category, models)
    final_ratings=[]

    # The weighted and liked/similarity ratings are combined as each are 50% of total score, so are combined here for the final score

    if liked_item_ratings == []:
        for i in range(len(weighted_ratings)):
            final_ratings.append([weighted_ratings[i][0], weighted_ratings[i][1]])

    else:
        for x in range(len(weighted_ratings)):

            total_rating=weighted_ratings[x][0] + liked_item_ratings[x][0]
            final_ratings.append([total_rating, weighted_ratings[x][1]])

    # Mergesort that takes in [[rating1, part1], [rating2, part2]] list
    sorted_list = return_sorted_list(final_ratings)
    
    for j in range(len(sorted_list)):
        for l in range(len(models)):
            if sorted_list[j][1] == models[l].id:
                sorted_models.append(models[l])
            
            
    return sorted_models

def weighting(parts, category, models):

    # This function rates items based on their features and the importance of each feature. This will be used client side 
    # to push specific items. So for example if the client wants to push expensive items, the price would be weighed higher
    # To boost it above cheaper items, even if the other items are more similar to the users likes
    
    # should iterate through each part and then weight stuff like sponsor status, num of likes it has etc and return a value 0-1
    weighted_ratings=[]

    likes=[]
    prices=[]
    sponsor_status=[]
    variations=[]

    for x in range(len(parts)):

        category=parts[x]['category']

        # Here it gets likes, prices and sponsor status for each part as well as the number of variations where applicable 
        # (Spoilers do not have size and colour variations)

        with connection.cursor() as sql:
            sql.execute(f"SELECT COUNT(*) FROM User_likes WHERE liked_part_id='{parts[x]['id']}'")
            num_liked=sql.fetchall()[0][0]
        likes.append(num_liked)

        price = parts[x]['price']
        prices.append(price)

        is_sponsored = parts[x]['is_sponsored']
        sponsor_status.append(is_sponsored)

        link_table_name= f"{category}_link_table"

        with connection.cursor() as sql:
            sql.execute(f"SELECT count(*) FROM pg_tables WHERE schemaname = 'public' AND tablename = %s", (link_table_name,))
            link_table_exists = bool(sql.fetchone()[0])

        if link_table_exists:
            
            with connection.cursor() as sql:
                sql.execute(f"SELECT COUNT(*) FROM {category}_link_table WHERE {category}_id='{parts[x]['id']}'")
                num_of_variations=sql.fetchall()[0][0]
            variations.append(num_of_variations)

        else:
            variations.append(0)

    # Reshape all feature lists to 2D arrays for MinMaxScaler
    likes_array = np.array(likes).reshape(-1, 1)
    prices_array = np.array(prices).reshape(-1, 1)
    sponsor_status_array = np.array(sponsor_status).reshape(-1, 1)
    variations_array = np.array(variations).reshape(-1, 1)

    # Scaler would scale the values between 0 and 1
    scaler = MinMaxScaler()
    scaled_likes = scaler.fit_transform(likes_array)
    scaled_prices = scaler.fit_transform(prices_array)

    if variations_array.size > 0:
        scaled_variations = scaler.fit_transform(variations_array)
    else:
        scaled_variations = None
    
    for x in range(len(parts)):

        # Applies the weights to the scaled values to promote different features
        weights=[models[x].like_weight, models[x].price_weight, models[x].sponsor_weight, models[x].variations_weight]
        weighted_liked = scaled_likes[x][0] * weights[0]
        weighted_price = scaled_prices[x][0] * weights[1]
        weighted_sponsor = sponsor_status[x] * weights[2]

        if scaled_variations is not None:
            weighted_variations = scaled_variations[x][0] * weights[3]
            weighted_rating = weighted_liked + weighted_price + weighted_sponsor + weighted_variations
        else:
            weighted_rating = weighted_liked + weighted_price + weighted_sponsor

        weighted_ratings.append([weighted_rating*0.5, parts[x]["id"]])

    # Returns a list of [rating, part_id] pairs
    return weighted_ratings


def liked_item_comparison(parts, user_id):

    # This function compares the parts to the users liked items and promotes items which are most similar to the liked items
    # This function is useful, however is limited due to the little data it has to work with, which is why it is used alongside
    # the weighting function. 
    # This also uses some collaborative recommendations by also comparing liked parts from similar users (ie users with similar cars)
    # and weighting them according to the relative similarity between the users

    
    liked_item_similarity=[]

    # Getting car data to calculate user similarity
    with connection.cursor() as sql:
        sql.execute(f"SELECT car_id FROM User_accounts WHERE account_id = '{user_id}'")
        user_car_id=sql.fetchone()

        sql.execute(f"SELECT * FROM Vehicle_Models WHERE vehicle_model_id = '{user_car_id[0]}'")
        user_car=sql.fetchall()

        sql.execute(f"SELECT car_id FROM User_accounts")
        other_car_ids = sql.fetchall()
        other_car_ids = [user[0] for user in other_car_ids]
        other_car_ids=tuple(other_car_ids)

        sql.execute(f"SELECT * FROM Vehicle_Models WHERE vehicle_model_id IN {other_car_ids}")
        similar_cars = sql.fetchall()

    # similar cars is a list of all the cars and their data which belong to users
    # user car is the data of the users car

    similar_car_id=[]
    user_similarities=[]

    for x in range(len(similar_cars)):
        
        # Here it compares other users cars to the users car, and finds the relative similarity and uses that as the user similarity rating

        similar_car_id.append(similar_cars[x][0])
        similar_car_data = similar_cars[x][1:]
        user_car_data = user_car[0][1:]

        necessary_fields = ['Make', 'Model', 'Year', "Drive", "Cylinders", "Engine displacement", "Transmission", "Vehicle Size Class"]
       
        similar_car_dict = dict(zip(necessary_fields, similar_car_data))
        user_car_dict = dict(zip(necessary_fields, user_car_data))

        dict_vectorizer = DictVectorizer()
        similar_car_vector = dict_vectorizer.fit_transform([similar_car_dict]).toarray()
        user_car_vector = dict_vectorizer.transform([user_car_dict]).toarray()

        user_similarities.append(cos_similarity(similar_car_vector, user_car_vector))
    
    # Scaling user similarities for relative similarity, since every pure rating is like 0.99999313

    user_similarities=np.array(user_similarities)
    scaler = MinMaxScaler()
    user_similarities = scaler.fit_transform(user_similarities)
    similar_car_id_tuple=tuple(similar_car_id)

    similar_user_ids=[]

    # Getting the ids of the users who own the cars, I have to use a for loop to maintain order 

    with connection.cursor() as sql:
        for x in range(len(similar_car_id)):
            sql.execute(f"SELECT account_id FROM User_accounts WHERE car_id = '{similar_car_id_tuple[x]}'")
            similar_user_ids.append(sql.fetchall()[0][0])

    user_ids=[]

    for x in range(len(similar_user_ids)):
        if similar_user_ids[x] == user_id:
            user_similarities = np.delete(user_similarities, x)
        else:
            user_ids.append(similar_user_ids[x])
    
    similar_user_ids=tuple(user_ids)

    similarity_id_pair=[]
    for x in range(len(user_similarities)):
        similarity_id_pair.append([user_similarities[x], similar_user_ids[x]])

    sorted_ids= return_sorted_list(similarity_id_pair)


    with connection.cursor() as sql:
        sql.execute(f"SELECT liked_part_id FROM User_likes WHERE account_id = '{user_id}'")
        liked_ids=sql.fetchall()

    similar_like_ids=set()
    if liked_ids:
        liked_ids = set(row[0] for row in liked_ids)

    sim_sum=0
    for x in range(len(sorted_ids)):
        sim_sum += sorted_ids[x][0]  
        with connection.cursor() as sql:
            sql.execute(f"SELECT liked_part_id FROM User_likes WHERE account_id = '{sorted_ids[x][1]}'")
            current_similar_like_ids = [row[0] for row in sql.fetchall()]  # Flatten to a list of IDs
            # Only consider IDs not already in liked_ids or similar_like_ids
            new_ids = [id for id in current_similar_like_ids if id not in liked_ids and id not in similar_like_ids]
            if new_ids:
                similar_like_ids.update(new_ids)  # Add all new IDs to the set

    avg_similarity = sim_sum / len(sorted_ids)
    similar_len = len(similar_like_ids) 

    comparison_part_ids = list(dict.fromkeys(list(similar_like_ids) + list(liked_ids)))

    for x in range(len(parts)):

        cos_values=[]
        liked_prices=[]

        # Creates a list of the prices of the liked items, which will be used to scale with the prices of the parts

        # Here 2 for loops are used to collect all the prices first, then to do the content similarity rating

        for j in range(len(comparison_part_ids)):

            with connection.cursor() as sql:
                sql.execute(f"SELECT price FROM Parts WHERE part_id='{comparison_part_ids[j]}'")
                liked_prices.append([sql.fetchall()[0][0]])

        liked_prices.append([parts[x]["price"]])

        for i in range(len(comparison_part_ids)):

            # Gets relevant data from the liked items and the current part

            with connection.cursor() as sql:
                sql.execute(f"SELECT * FROM Parts WHERE part_id='{comparison_part_ids[i]}'")
                relevant_items=sql.fetchall()

            relevant_fields = ['category', 'item_name', 'merchant_name', 'image_url', 'price']
            current_part_data=[str(parts[x][key]) for key in relevant_fields]
            liked_part_data=list(map(str, relevant_items[0][1:-1])) # This is just to turn it into the same format as the current part data

            # Use separate TfidfVectorizer instances for current and liked data
            # The vectorizer is used to convert the text data into a matrix of numbers 
            current_vectorizer = TfidfVectorizer(max_features=4)
            liked_vectorizer = TfidfVectorizer(max_features=4)

            current_part_array = current_vectorizer.fit_transform(current_part_data).toarray()
            liked_part_array = liked_vectorizer.fit_transform(liked_part_data).toarray()
            num_array = np.array(liked_prices)

            # The scaler is used to scale the values of the items to be between 0 and 1

            scaler = MinMaxScaler()
            scaled_prices = scaler.fit_transform(num_array)
            
            # This is done to add in the price arrays which were treated seperately 

            current_part_array = np.insert(current_part_array, [0], scaled_prices[-1], axis=1)
            liked_part_array = np.insert(liked_part_array, [0], scaled_prices[i], axis=1)

            # Reshape the arrays to 2D for cosine similarity calculation

            current_part_array=current_part_array.reshape(1, -1)
            liked_part_array=liked_part_array.reshape(1, -1)

            # Cosine similarity is used to compare the two arrays, which gives a value between 0 and 1 based on how similar they are
            # The closer to 1, the more similar they are
            if i <= similar_len-1:
                cos_values.append(cos_similarity(current_part_array, liked_part_array)[0]*avg_similarity)
            else:
                cos_values.append(cos_similarity(current_part_array, liked_part_array)[0])

        liked_item_similarity.append([0.5*(math.fsum(cos_values)/len(cos_values)), parts[x]["id"]])

    # Returns a list of [rating, part_id] pairs to the list

    return liked_item_similarity
