import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper

# Alternatively you can import a specific function or class
from apper import AppObjects

import json

import vex_cad

allParameterManagers = []

def defineParameterManagers():
    ao = AppObjects()
    unitsMgr = ao.units_manager

    class ConvertCustomUnits:
        def __init__(self, ratio):
            self.ratio = ratio
        def value(self, input):
            return unitsMgr.evaluateExpression(input + self.ratio, '')

    inToHoles = ConvertCustomUnits('/0.5in')
    holesToIn = ConvertCustomUnits('*0.5in')

    class ParameterManager:
        def __init__(self, id, name):
            self.id = id
            self.name = name
        # Defaults
        def hide(self):
            self.commandInput.isVisible = False
        def onUpdate(self, comp):
            pass

        # Need to be redefined
        def create(self, commandInputs):
            pass
        def show(self, comp):
            pass
        def updatePart(self, comp):
            pass
    
    class FloatSpinnerDistanceHolesV1(ParameterManager):
        def create(self, commandInputs):
            self.commandInput = commandInputs.addFloatSpinnerCommandInput(self.id, self.name, '', 1, 35, 1, 1)
        def show(self, comp):
            parameter = vex_cad.getPartData(comp)['parameters'][self.id]
            index = parameter['index']
            self.commandInput.expression = str(inToHoles.value(comp.modelParameters.item(index).expression))
            
            self.commandInput.isVisible = True
            self.onUpdate(comp)
        def onUpdate(self, comp):
            parameter = vex_cad.getPartData(comp)['parameters'][self.id]
            if self.commandInput.value > parameter['max_value']:
                self.commandInput.value = parameter['max_value']

        def updatePart(self, comp):
            parameter = vex_cad.getPartData(comp)['parameters'][self.id]
            comp.modelParameters.item(parameter['index']).value = holesToIn.value(self.commandInput.expression)
    
    return [
        # FloatSpinnerDistanceOffsetHolesV1('length_holes_offset_v1', 'Length Holes'),
        # FloatSpinnerDistanceOffsetHolesV1('width_holes_offset_v1', 'Width Holes'),
        FloatSpinnerDistanceHolesV1('length_holes_v1', 'Length Holes'),
        FloatSpinnerDistanceHolesV1('width_holes_v1', 'Width Holes')]


def createAllCommandInputs(commandInputs):
    global allParameterManagers
    allParameterManagers = {parameterManager.id: parameterManager for parameterManager in defineParameterManagers()}
    for parameterManager in allParameterManagers:
        allParameterManagers[parameterManager].create(commandInputs)

def hideAllCommandInputs():
    for parameterManager in allParameterManagers:
        allParameterManagers[parameterManager].hide()

def parameterManagersInParameters(comp):
    parameters = vex_cad.getPartData(comp)['parameters']
    return [allParameterManagers[parameter] for parameter in parameters if parameter in allParameterManagers]

def showSomeCommandInputs(comp):
    for parameterManager in parameterManagersInParameters(comp):
        parameterManager.show(comp)

def updateInputs(comp):
    for parameterManager in parameterManagersInParameters(comp):
        parameterManager.onUpdate(comp)

def updatePart(comp):
    for parameterManager in parameterManagersInParameters(comp):
        parameterManager.updatePart(comp)











# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class ModifyPart(apper.Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):

        # updating parts with 1600+ faces every change doesn't go well.
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        
        app = adsk.core.Application.get()

        selectionInput = inputs.itemById('selection_input_id')

        selectionInput = inputs.itemById('selection_input_id')
        if selectionInput.selectionCount > 0:
            selectedComp = vex_cad.getCompIfOccurrence(selectionInput.selection(0).entity)
            if selectedComp.attributes.itemByName('vex_cad', 'part_data'):
                selectedCompAttributes = vex_cad.getPartData(selectedComp)
                if changed_input.id == 'selection_input_id':
                    if 'parameters' in selectedCompAttributes:
                        showSomeCommandInputs(selectedComp)
                else:
                    if 'parameters' in selectedCompAttributes:
                        updateInputs(selectedComp)
            else:
                selectionInput.clearSelection()
        else:
            hideAllCommandInputs()

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        selectionInput = inputs.itemById('selection_input_id')
        selectedEntity = selectionInput.selection(0).entity
        if selectedEntity.objectType == 'adsk::fusion::Occurrence' and selectedEntity.isReferencedComponent:
            selectedEntity.breakLink()
        comp = vex_cad.getCompIfOccurrence(selectedEntity)
        updatePart(comp)

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

        createAllCommandInputs(inputs)
        hideAllCommandInputs()

