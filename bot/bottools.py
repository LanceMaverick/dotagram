#for first key match in list of dicts
def keySearch(lst,key,value):
    for item in lst:
        if item[key] == value:
            return item
    return None    
