import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper

def getCompIfOccurrence(entity):
    if entity.objectType == 'adsk::fusion::Occurrence':
        return entity.component
    else: 
        return entity