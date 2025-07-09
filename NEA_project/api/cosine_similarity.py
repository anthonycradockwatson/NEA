import math

def cos_similarity(a, b): # a cosine similarity formula to compare 2 vectors a and b
    if len(a) == 0 or len(b) == 0:
        return "Cannot compare empty arrays"
    
    elif len(a[0]) != len(b[0]):
            return "List A needs to be the same length as list B"

    a_squared=[]
    b_squared=[]
    dot_product=[]

    for x in range(len(a[0])):

        a_squared.append(math.pow(a[0][x], 2))
        b_squared.append(math.pow(b[0][x], 2))
        dot_product.append(a[0][x]*b[0][x])

    a_l2_norm = math.sqrt(math.fsum(a_squared))
    b_l2_norm= math.sqrt(math.fsum(b_squared))
    dot_product=math.fsum(dot_product)

    ab_l2_norm=a_l2_norm*b_l2_norm

    similarity=dot_product/ab_l2_norm

    return [round(similarity, 10)]




