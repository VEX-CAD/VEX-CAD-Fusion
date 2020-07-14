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

    class FloatSpinnerDistanceOffsetHoles_1_0_0(Input):
        def create(self, commandInputs):
            self.inputDistance = commandInputs.addFloatSpinnerCommandInput(self.id + 'Distance', self.name, '', 0, 35, 1, 0)
            self.inputOffset = commandInputs.addFloatSpinnerCommandInput(self.id + 'Offset', 'Offset Holes', '', 0, 35, 1, 0)
        def show(self, parameter):
            self.parameter = parameter
            index_distance = self.parameter['index_distance']
            index_offset = self.parameter['index_offset']
            self.inputDistance.expression = str(inToHoles.value(selectedComp.modelParameters.item(index_distance).expression))
            self.inputOffset.expression = str(inToHoles.value(selectedComp.modelParameters.item(index_offset).expression))
            
            self.inputDistance.isVisible = True
            self.inputOffset.isVisible = True
            self.onUpdate()
        def hide(self):
            self.inputDistance.isVisible = False
            self.inputOffset.isVisible = False
        def onUpdate(self):
            if self.inputDistance.value > self.parameter['max_value']:
                self.inputDistance.value = self.parameter['max_value']

            if self.inputDistance.value + self.inputOffset.value > self.parameter['max_value']:
                self.inputOffset.value = self.parameter['max_value'] - self.inputDistance.value
        def updatePart(self, comp):
            comp.modelParameters.item(self.parameter['index_distance']).value = holesToIn.value(self.inputDistance.expression)
            comp.modelParameters.item(self.parameter['index_offset']).value = holesToIn.value(self.inputOffset.expression)
    
    class FloatSpinnerDistanceHoles_1_0_0(Input):
        def create(self, commandInputs):
            self.input = commandInputs.addFloatSpinnerCommandInput(self.id + 'Distance', self.name, '', 0, 35, 1, 0)
        def show(self, parameter):
            self.parameter = parameter
            index = self.parameter['index']
            self.input.expression = str(inToHoles.value(selectedComp.modelParameters.item(index).expression))
            
            self.input.isVisible = True
            self.onUpdate()
        def onUpdate(self):
            if self.input.value > self.parameter['max_value']:
                self.input.value = self.parameter['max_value']

        def updatePart(self, comp):
            comp.modelParameters.item(self.parameter['index']).value = holesToIn.value(self.input.expression)
    
    return [
        FloatSpinnerDistanceHoles_1_0_0('length_holes_1_0_0', 'Length Holes'),
        FloatSpinnerDistanceHoles_1_0_0('width_holes_1_0_0', 'Width Holes'),
        FloatSpinnerDistanceOffsetHoles_1_0_0('length_holes_offset_1_0_0', 'Length Holes'),
        FloatSpinnerDistanceOffsetHoles_1_0_0('width_holes_offset_1_0_0', 'Width Holes')]


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

def updatePart(comp, parameters):
    if 'parameters' in parameters:
        for parameter in parameters['parameters']:
            allInputObjects[parameter].updatePart(comp)











# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class ModifyPart(apper.Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):

        # updating highgly parts with 3000+ faces every change doesn't go well.

        # updatePart(selectedComp, selectedCompAttributes)
        pass

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

        selectionInput = inputs.itemById('selection_input_id')
        if changed_input.id == 'selection_input_id':
            if selectionInput.selectionCount > 0:
                if selectionInput.selection(0).entity.objectType == 'adsk::fusion::Occurrence':
                    selectedComp = selectionInput.selection(0).entity.component
                else: 
                    selectedComp = selectionInput.selection(0).entity
                if selectedComp.attributes.count > 0 and selectedComp.attributes.itemByName('VFL', 'part_data'):
                    selectedCompAttributes = json.loads(selectedComp.attributes.itemByName('VFL', 'part_data').value)
                    if 'parameters' in selectedCompAttributes:
                        showSomeCommandInputs(selectedCompAttributes['parameters'])
                else:
                    selectionInput.clearSelection()
            else:
                selectionInput.clearSelection()
                selectedCompAttributes.clear()
                hideAllCommandInputs()
        else:
            if 'parameters' in selectedCompAttributes:
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
        selectionInput.setSelectionLimits(1, 1)
        selectionInput.addSelectionFilter('Occurrences')

        global allInputObjects
        allInputObjects = {inputObjects.id: inputObjects for inputObjects in defineInputs()}
        for inputObject in allInputObjects:
            allInputObjects[inputObject].create(inputs)
        hideAllCommandInputs()

