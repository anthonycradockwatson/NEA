
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .serializers import post_serializer
from .object_convert import object_converter
from .search_algorithm import Search
from .item_data import item_data
from .input_cleansing import input_cleansing
from .user_account_signup import user_signup_check
from .user_likes import user_liked
from .car_table_input import add_car
from .user_likes import user_liked, user_unlike
from .item_collect import item_collect
from .validate import validation, sql_check, all_categories

""" To do list:
seperate endpoints for 3d model items
 - add some like inner joins or smth

search_query = 
/api/get_search?query=rcing&user_id=2fdd047c-62d5-4ab4-95ba-a68f915a786f&category=Wheels&category=Spoilers&category=Grills

"""


@api_view(['GET'])

def get_search(request): 
    # Endpoint to handle searches
    query = request.query_params.get('query')
    category = request.query_params.getlist('category') # Collects the category from the request
    user_id=request.query_params.get('user_id') # Collects the user id from the request

    if category == None or query ==  None:
        return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_input= input_cleansing(query) # cleans prompt 

    if category != ["*"]: # allows for all categories to be accepted
        valid_request=validation(category)
    else:
        valid_request=True
        category=all_categories("category")
    
    if user_id is not None:
        valid_sql=sql_check(user_id, "User_accounts", "account_id")
    else:
        valid_sql=True

    if not valid_input:
       return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
    
    if valid_request == False or valid_sql == False:
         return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    search_instance=Search(query, category)
    keyword_results = search_instance.keyword_search() 
    fuzzy_results = search_instance.fuzzy_search(keyword_results) 
    results=[]

    # Does 2 different searches to ensure nothing is missed, makes sure that there are no repeats
     
    for x in range(len(keyword_results)):
        if keyword_results[x][0] not in results: 
            results.append(keyword_results[x][0])

    for i in range(len(fuzzy_results)):  
        if fuzzy_results[i][0] not in results:
            results.append(fuzzy_results[i][0]) 

    # Turns results into parts and subparts objects and sorts them by recommendations
    results=object_converter(results, user_id, category) 

    if results==None:
        return Response({"No results found"}, status=status.HTTP_200_OK)
    
    return Response(results, status=status.HTTP_200_OK) 

@api_view(['GET'])

def get_item_data(request):
    # When a user clicks on a specific part, it gets specific data like colour, size, part data etc
    part_id = request.query_params.get('part_id')

    if part_id ==  None:
        return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    valid_sql=sql_check(part_id, "Parts", "part_id")

    if valid_sql == False:
         return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)


    category, current_part, colour, size=item_data(part_id)
    # If there are sizes or colours, assign them to the part object
    current_part=current_part # Convert the part object to a list to append the colour and size
    if colour != []:
        current_part+=(colour,) # Append the colours or sizes if they exist to the part object

    if size != []:
        current_part+=(size,)

    current_part=[current_part]

    results=object_converter(current_part, None, category)

    if results==None:
        return Response({"No results found"}, status=status.HTTP_200_OK)

    return Response(results, status=status.HTTP_200_OK)

    
@api_view(['GET'])

def get_items(request):
    # Getting any items that meet the specifications

    category = request.query_params.getlist('category') 
    user_id= request.query_params.get('user_id') 
    manufacturers = request.query_params.getlist('manufacturers')
   
    if category == None or manufacturers ==  None:
        return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
    
    if category != ["*"]: # allows for all categories to be accepted
        valid_request=validation(category)
    else:
        valid_request=True
        category=all_categories("category")

    if manufacturers != ["*"]: # allows for all manufacturers to be accepted
        valid_sql2=sql_check(manufacturers, "Parts", "merchant_name")
    else:
        valid_sql2=True
        manufacturers=all_categories("merchant_name")
        
    if user_id is not None:
        valid_sql1=sql_check(user_id, "User_accounts", "account_id")
    else:
        valid_sql1=True


    if valid_request == False or valid_sql1 == False or valid_sql2 == False:
         return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    results=item_collect(category, manufacturers)
  
    final_results=object_converter(results, user_id, category) 

    if final_results==None:
        return Response({"No results found"}, status=status.HTTP_200_OK)
    
    return Response(final_results, status=status.HTTP_200_OK) 

@api_view(['POST'])

def post_user_signup(request):
    # Handling new users signing up

    request_body=post_serializer(request.body)
    email=request_body.get("email")
    password=request_body.get("password")
    car_make=request_body.get("car_make")
    car_model=request_body.get("car_model")
    car_year=request_body.get("car_year")
    car_cylinders=request_body.get("car_cylinders")
    car_engine_displacement=request_body.get("car_engine_displacement")
    car_transmission=request_body.get("car_transmission")

    valid_email=input_cleansing(email, True)
    valid_password=input_cleansing(password)
    
    if not valid_email or not valid_password:
       return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    # Adds the car and account seperately just in case didn't specify car or just linking new car to existing account
    car_id=add_car(car_make, car_model, car_year, car_cylinders, car_engine_displacement, car_transmission)
    signup=user_signup_check(email, password, car_id)

    if signup == True or car_id != None:
        return(Response(status=status.HTTP_201_CREATED))
    else:
        return(Response(status=status.HTTP_409_CONFLICT))

@api_view(['POST'])

def post_user_liked(request):
    # Addng user likes, here it gives a list of all the users likes and it just adds the ones that dont exist already.s

    request_body=post_serializer(request.body)

    part_id=request_body.get('part_id')
    user_id=request_body.get('user_id')

    if part_id == None or user_id ==  None:
        return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    valid_sql2=sql_check(part_id, "Parts", "part_id")

    if user_id is not None:
        valid_sql1=sql_check(user_id, "User_accounts", "account_id")
    else:
        valid_sql1=True

    if valid_sql1 == False or valid_sql2 == False:
         return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    like_added=user_liked(part_id, user_id)
    
    if like_added == True:
        return(Response(status=status.HTTP_201_CREATED))
    else:
        return(Response(status=status.HTTP_204_NO_CONTENT))

@api_view(['POST'])

def post_user_unliked(request):
    # Removing user likes

    request_body=post_serializer(request.body)

    part_id=request_body.get('part_id')
    user_id=request_body.get('user_id')
    
    if part_id == None or user_id ==  None:
        return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_sql2=sql_check(part_id, "Parts", "part_id")

    if user_id is not None:
        valid_sql1=sql_check(user_id, "User_accounts", "account_id")
    else:
        valid_sql1=True


    if valid_sql1 == False or valid_sql2 == False:
         return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    like_removed=user_unlike(part_id, user_id)
    
    if like_removed == True:
        return(Response(status=status.HTTP_204_NO_CONTENT))
    return Response({"Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)

    
