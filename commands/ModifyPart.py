import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper

# Alternatively you can import a specific function or class
from apper import AppObjects

import json

allInputObjects = []

selectedComp = None
selectedCompAttributes = None

def defineInputs():
    ao = AppObjects()
    unitsMgr = ao.units_manager

    class ConvertCustomUnits:
        def __init__(self, ratio):
            self.ratio = ratio
        def value(self, input):
            return unitsMgr.evaluateExpression(input + self.ratio, '')

    inToHoles = ConvertCustomUnits('/0.5in')
    holesToIn = ConvertCustomUnits('*0.5in')

    class Input:
        def __init__(self, id, name):
            self.id = id
            self.name = name
        def hide(self):
            self.input.isVisible = False
        def onUpdate(self):
            pass

    class FloatSpinnerDistanceOffsetHoles(Input):
        def create(self, commandInputs):
            self.inputDistance = commandInputs.addFloatSpinnerCommandInput(self.id + 'Distance', self.name, '', 0, 40, 1, 0)
            self.inputOffset = commandInputs.addFloatSpinnerCommandInput(self.id + 'Offset', 'Offset Holes', '', 0, 40, 1, 0)
        def show(self, parameter):
            self.parameter = parameter
            # self.inputDistance.minimumValue = self.parameter['minValue']
            # self.inputDistance.maximumValue = self.parameter['maxValue']
            indexDistance = self.parameter['indexDistance']
            indexOffset = self.parameter['indexOffset']
            self.inputDistance.expression = str(inToHoles.value(selectedComp.modelParameters.item(indexDistance).expression))
            self.inputOffset.expression = str(inToHoles.value(selectedComp.modelParameters.item(indexOffset).expression))
            
            self.inputDistance.isVisible = True
            self.inputOffset.isVisible = True
            self.onUpdate()
        def hide(self):
            self.inputDistance.isVisible = False
            self.inputOffset.isVisible = False
        def onUpdate(self):
            # if self.inputDistance.value > self.parameter['maxValue']:
            #     self.inputDistance.value = self.parameter['maxValue']

            # if self.inputDistance.value + self.inputOffset.value > self.parameter['maxValue']:
            #     self.inputOffset.value = self.parameter['maxValue'] - self.inputDistance.value

            # inputDistanceFloat = unitsMgr.evaluateExpression(self.inputDistance.expression, '')
            # if inputDistanceFloat > inToHoles.value(selectedComp.modelParameters.item(indexDistance).expression):
            # print(inputDistanceFloat)
            # if inputDistanceFloat > self.parameter['maxValue']:
            #     self.inputDistance.expression = str(self.parameter['maxValue'])
            #     self.onUpdate()
            # if inputDistanceFloat > self.parameter['maxValue']:
            #     self.inputDistance.expression = str(self.parameter['maxValue'])
            #     self.onUpdate()
        def updatePart(self, comp):
            comp.modelParameters.item(self.parameter['indexDistance']).value = holesToIn.value(self.inputDistance.expression)
            comp.modelParameters.item(self.parameter['indexOffset']).value = holesToIn.value(self.inputOffset.expression)
    
    return [
        FloatSpinnerDistanceOffsetHoles('FloatSpinnerDistanceOffsetHolesLength', 'Length Holes'),
        FloatSpinnerDistanceOffsetHoles('FloatSpinnerDistanceOffsetHolesWidth', 'Width Holes')]


def createAllCommandInputs(commandInputs):
    pass

def hideAllCommandInputs():
    for input in allInputObjects:
        allInputObjects[input].hide()

def showSomeCommandInputs(parameters):
    for parameter in parameters:
        allInputObjects[parameter].show(parameters[parameter])

def updateInputs(parameters):
        for parameter in parameters:
            allInputObjects[parameter].onUpdate()

def updateModelParameter(comp, parameters):
    comp.modelParameters.item(parameters['indexMP']).expression = parameters['value']

def updateBodyBulbs(comp, parameters):
    for key, value in parameters.items():
        comp.bRepBodies.itemByName(key).isLightBulbOn = value

def updateInserts(comp, parameters):
    # print(parameters)
    if parameters['value'] == 'None':
        updateBodyBulbs(comp, {'Square Insert 1': False, 'Square Insert 2': False, 'Round Insert 1': False, 'Round Insert 2': False})
    elif parameters['value'] == 'Square':
        updateBodyBulbs(comp, {'Square Insert 1': True, 'Square Insert 2': True, 'Round Insert 1': False, 'Round Insert 2': False})
    elif parameters['value'] == 'Round':
        updateBodyBulbs(comp, {'Square Insert 1': False, 'Square Insert 2': False, 'Round Insert 1': True, 'Round Insert 2': True})


def updatePart(comp, parameters):
    # print('updatePart: ')
    # print(comp)
    for parameter in parameters['parameters']:
        allInputObjects[parameter].updatePart(comp)

    # for key, value in parameters.items():
    #     if key == 'lengthHoles':
    #         updateModelParameter(comp, value)
    #     elif key == 'widthHoles':
    #         updateModelParameter(comp, value)
    #     elif key == 'inserts':
    #         updateInserts(comp, value)
















# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class ModifyPart(apper.Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        updatePart(selectedComp, selectedCompAttributes)

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        
        app = adsk.core.Application.get()
        global selectedComp
        global selectedCompAttributes


        selectionInput = inputs.itemById('selection_input_id')

        if changed_input.id == 'selection_input_id':
            if selectionInput.selectionCount == 1 and app.activeProduct.rootComponent != selectionInput.selection(0).entity:
                selectedComp = selectionInput.selection(0).entity.component
                if selectedComp and selectedComp.attributes.count > 0 and selectedComp.attributes.itemByName('VFL', 'partData'):
                    selectedCompAttributes = json.loads(selectedComp.attributes.itemByName('VFL', 'partData').value)
                    showSomeCommandInputs(selectedCompAttributes['parameters'])

                else:
                    selectionInput.clearSelection()
            else:
                selectionInput.clearSelection()
                selectedCompAttributes.clear()
                hideAllCommandInputs()
        else:
            updateInputs(selectedCompAttributes['parameters'])

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):

        updatePart(selectedComp, selectedCompAttributes)

    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        ao = AppObjects()

        # Create a default value using a string
        default_value = adsk.core.ValueInput.createByString('1.0 in')

        # Get teh user's current units
        default_units = ao.units_manager.defaultLengthUnits

        selectionInput = inputs.addSelectionInput('selection_input_id', 'Select Parametric Part', 'Component to select')
        selectionInput.setSelectionLimits(1, 0)
        selectionInput.addSelectionFilter('Occurrences')

        global allInputObjects
        allInputObjects = {inputObjects.id: inputObjects for inputObjects in defineInputs()}
        for inputObject in allInputObjects:
            allInputObjects[inputObject].create(inputs)
        hideAllCommandInputs()

