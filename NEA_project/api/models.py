from django.db import models
from typing import Optional
from dataclasses import dataclass, asdict

# Create your models here.
@dataclass
class Search():
    search: str

    def __init__(self, search):
        self.search=search

@dataclass
class Colour_stack():
    available_colours: list[str]

    def __init__(self, colour_list: list[str]):
        self.available_colours = colour_list

@dataclass
class Size_stack():
    size: list[int]
    size_unit: str

    def __init__(self, size_unit: str, available_sizes: list[int]):
        self.size = available_sizes
        self.size_unit = size_unit

@dataclass
class Part():
    id: str
    category: str
    item_name: str
    merchant_name: str
    image_url: str
    price: str
    is_sponsored: bool
    colour: Optional[Colour_stack] = None  
    size: Optional[Size_stack] = None 

    def __init__(self, id, category, item_name, merchant_name, image_url, price, is_sponsored, colour=[], size=[]):  # Part models for returning
        self.id = id
        self.category=category
        self.item_name = item_name
        self.merchant_name = merchant_name
        self.image_url = image_url
        self.price = price
        self.is_sponsored = is_sponsored
        self.colour = colour
        self.size = size

class Wheels(Part):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.like_weight = 0.20
        self.price_weight = 0.20
        self.sponsor_weight = 0.45
        self.variations_weight = 0.15

class Spoilers(Part):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.like_weight = 0.35
        self.price_weight = 0.4
        self.sponsor_weight = 0.25
        self.variations_weight = 0

class Front_bumpers(Part):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.like_weight = 0.20
        self.price_weight = 0.25
        self.sponsor_weight = 0.40
        self.variations_weight = 0.15

class Rear_bumpers(Part):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.like_weight = 0.15
        self.price_weight = 0.25
        self.sponsor_weight = 0.45
        self.variations_weight = 0.15

class Grills(Part):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.like_weight = 0.20
        self.price_weight = 0.25
        self.sponsor_weight = 0.40
        self.variations_weight = 0.15 