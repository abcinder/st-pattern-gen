def parseBooleanString(string):
    return string[0].upper() == 'T'

def printList(list):
    for num, item in enumerate(list):
        print num, ' ', item