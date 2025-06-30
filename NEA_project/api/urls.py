from django.urls import path
from .views import get_search, get_item_data, get_items, post_user_signup, post_user_liked, post_user_unliked
# API urls are used for more specific endpoints 
urlpatterns = [
    path('search/', get_search, name='search'),
    path('item-data/', get_item_data, name='item_data'),
    path('user-signup/', post_user_signup, name='user-signup'),
    path('user-liked/', post_user_liked, name='user-liked'),
    path('user-like-removed/', post_user_unliked, name='user-unliked'),
    path('collect-items/', get_items, name='collect_items')
]
