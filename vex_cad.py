import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper
import json

def getCompIfOccurrence(entity):
    if entity.objectType == 'adsk::fusion::Occurrence':
        return entity.component
    return entity

def getPartData(comp):
    return json.loads(comp.attributes.itemByName('vex_cad', 'part_data').value)