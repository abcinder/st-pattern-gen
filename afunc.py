import os

''' MISC FUNCTIONS ''' 
def parseBooleanString(string):
    return string[0].upper() == 'T'

def printList(list):
    for num, item in enumerate(list):
        print num, ' ', item
        

''' FILE I/O '''
def openFile(name, mode='wb'):
    name = str(name)
    file = open(name, mode)
    print "Created file: ", file.name
    return file

def closeFile(file):
    file.close()
    print "Closed file: " + file.name

def removeFile(path):
    print ''
    print "Removed file: " + path
    print ''
    os.remove(path)