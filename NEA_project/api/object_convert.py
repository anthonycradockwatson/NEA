from .recommendations import recommendation
from .serializers import item_json
from .models import Part, Wheels, Spoilers, Front_Bumpers, Rear_Bumpers, Grills

def object_converter(results, user_id, category):

    result_models=[]
    part_types = {
        "Wheels": Wheels,
        "Spoilers": Spoilers,
        "Front_Bumpers": Front_Bumpers,
        "Rear_Bumpers": Rear_Bumpers,
        "Grills": Grills
    }
    # Loop through all the results and create a Part object for each one
    if results: # If results are found, create a list of part objects to be returned
            for x in range(len(results)):
                
                current_part=results[x]
                part_data = {
                    "id": current_part[0],
                    "category": current_part[1],
                    "item_name": current_part[2],
                    "merchant_name": current_part[3],
                    "image_url": current_part[4],
                    "price": current_part[5],
                    "is_sponsored": current_part[6],
                    "colour": current_part[7] if len(current_part) > 7 else [], # dynamically assigns colour and size specs when needed
                    "size": current_part[8] if len(current_part) > 8 else []
                }
                category = part_data["category"]
                part_class=part_types.get(category, Part)
                result_model=part_class(**part_data)
                result_models.append(result_model) 
    
    if result_models == []: # If no results are found, return no results found
        return  None
    
    if len(result_models) > 1:
        recommend_parts=recommendation(result_models, user_id, category)
    else:
        recommend_parts=result_models

    json_results = []
    for x in range(len(recommend_parts)): # Loop through all the results and serialize them to be returned

        serialized_return=item_json(recommend_parts[x]) # Otherwise serialize the objects and return them
        json_results.append(serialized_return)

    return json_results
