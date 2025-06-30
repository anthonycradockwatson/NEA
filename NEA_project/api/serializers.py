import json
from dataclasses import asdict

def post_serializer(data):
    return json.loads(data)

def item_json(part):
    # Serializes part objects into json to be returned to the frontend
    if part.colour:
        part.colour = [x.strip('"') for x in part.colour] # Removes quotes from the colour strings

    json_string=json.dumps(asdict(part), indent=2)
    json_item=json.loads(json_string)
    # Turn the dataclass into a dictionary and then into a json string to be returned to the frontend
    return json_item

