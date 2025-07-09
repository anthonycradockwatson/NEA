
def merge_pairs(list1, list2):
    temp_list = []
    while list1 != [] and list2 != []: # keeps going as long as both lists aren't empty
        # Compare by rating (first element of each pair)
        if list1[0][0] < list2[0][0]:
            temp_list.append(list2.pop(0))
        else:
            temp_list.append(list1.pop(0))

    return temp_list + list1 + list2

def merge_sort_pairs(pair_list):
    # recursively breaks everything down to be one thing, then compares each item, sorting them
    if len(pair_list) <= 1:
        return pair_list
    
    mid = len(pair_list) // 2
    left = merge_sort_pairs(pair_list[:mid])
    right = merge_sort_pairs(pair_list[mid:])

    return merge_pairs(left, right)

def return_sorted_list(original_list):
    # Sorts [rating, item] pairs by rating
    return merge_sort_pairs(original_list)
