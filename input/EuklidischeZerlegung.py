


def euklid(a,b):

    # Faktorenzerlegung

    print("IN euklid: ", a, b)

    if a == b:
        print ("GGT: ", a, b)
    elif a < b:
        euklid(b-a, a)
    else:
        euklid(a-b, b)


print(462 % (3 * 147))

def euklid2(a,b):
    if b == 0:
        print("GGT euklid2" , a)
    else:
        euklid2(b, a % b)


#
euklid(1071, 462)

euklid2(1071, 462)

euklid2(1071, 1029)
euklid(1071, 1029)