import numpy as np

def merge(list1, list2):

    temp_list = []

    while len(list1) != 0 and len(list2) != 0:
        if list1[0] < list2[0]:

            temp_list.append(list2.pop(0))

        else:

            temp_list.append(list1.pop(0))

    return temp_list + list1 + list2

def merge_sort_full(num_list):

    if len(num_list) <= 1:
        return num_list
    
    mid = len(num_list) // 2
    left = merge_sort_full(num_list[:mid])
    right = merge_sort_full(num_list[mid:]) 
    return merge(left, right)

def return_sorted_list(original_list):

    values = [item[0] for item in original_list]

    sorted_values = merge_sort_full(values)

    final_ratings = []

    for x in range(len(sorted_values)):
        for i in range(len(original_list)):

            if original_list[i][0] == sorted_values[x] and original_list[i] not in final_ratings:

                final_ratings.append(original_list[i])
                break
            
    return final_ratings

