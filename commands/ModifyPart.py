import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper
# import config

# Alternatively you can import a specific function or class
# from apper import apper.AppObjects

import json
# from .modules import keyboard
import keyboard

import vex_cad

allParameterManagers = []

def defineParameterManagers():
    ao = apper.AppObjects()
    unitsMgr = ao.units_manager

    class ConvertCustomUnits:
        def __init__(self, ratio):
            self.ratio = ratio
        def value(self, input):
            return unitsMgr.evaluateExpression(input + self.ratio, '')

    def setInsertLightBulb(comp, insertType, isOn):
        for i in range(comp.occurrences.count):
            subComp = comp.occurrences.item(i).component
            if subComp.attributes.itemByName('vex_cad', 'part_data') and 'identifiers' in vex_cad.getPartData(subComp):
                identifiers = vex_cad.getPartData(subComp)['identifiers']
                if 'insert' in identifiers:
                    if insertType in identifiers['insert']:
                        subComp.isBodiesFolderLightBulbOn = isOn
    
    def iSInsertVisible(comp, insertType):
        for i in range(comp.occurrences.count):
            subComp = comp.occurrences.item(i).component
            if subComp.attributes.itemByName('vex_cad', 'part_data') and 'identifiers' in vex_cad.getPartData(subComp):
                identifiers = vex_cad.getPartData(subComp)['identifiers']
                if 'insert' in identifiers:
                    if insertType in identifiers['insert']:
                        return subComp.isBodiesFolderLightBulbOn

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
        def previewUpdatePart(self, comp):
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
    
    class ButtonRowInsertsV1(ParameterManager):
        def create(self, commandInputs):
            self.commandInput = commandInputs.addButtonRowCommandInput(self.id, self.name, False)
            # self.commandInput.listItems.add('None', True, 'commands/resources/command_icons/insert_none')
            # self.commandInput.listItems.add('Square', False, 'commands/resources/command_icons/insert_square')
            # self.commandInput.listItems.add('Round', False, 'commands/resources/command_icons/insert_round')
        
        def show(self, comp):
            self.commandInput.listItems.clear()
            if iSInsertVisible(comp, 'round') and not iSInsertVisible(comp, 'square'):
                self.commandInput.listItems.add('None', False, 'commands/resources/command_icons/insert_none')
                self.commandInput.listItems.add('Square', False, 'commands/resources/command_icons/insert_square')
                self.commandInput.listItems.add('Round', True, 'commands/resources/command_icons/insert_round')
            elif iSInsertVisible(comp, 'square') and not iSInsertVisible(comp, 'round'):
                self.commandInput.listItems.add('None', False, 'commands/resources/command_icons/insert_none')
                self.commandInput.listItems.add('Square', True, 'commands/resources/command_icons/insert_square')
                self.commandInput.listItems.add('Round', False, 'commands/resources/command_icons/insert_round')
            else:
                self.commandInput.listItems.add('None', True, 'commands/resources/command_icons/insert_none')
                self.commandInput.listItems.add('Square', False, 'commands/resources/command_icons/insert_square')
                self.commandInput.listItems.add('Round', False, 'commands/resources/command_icons/insert_round')
            self.commandInput.isVisible = True

        # def previewUpdatePart(self, comp):
        #     self.updatePart(comp)

        def updatePart(self, comp):
            # parameter = vex_cad.getPartData(comp)['parameters'][self.id]
            # comp.modelParameters.item(parameter['index']).value = holesToIn.value(self.commandInput.expression)
            itemName = self.commandInput.selectedItem.name
            if itemName == 'None':
                setInsertLightBulb(comp, 'square', False)
                setInsertLightBulb(comp, 'round', False)
            elif itemName == 'Square':
                setInsertLightBulb(comp, 'square', True)
                setInsertLightBulb(comp, 'round', False)
            elif itemName == 'Round':
                setInsertLightBulb(comp, 'square', False)
                setInsertLightBulb(comp, 'round', True)
    
    return [
        ButtonRowInsertsV1('inserts_v1', 'Inserts'),
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
    keyboard.press_and_release('tab')

def updateInputs(comp):
    for parameterManager in parameterManagersInParameters(comp):
        parameterManager.onUpdate(comp)

def updatePart(comp):
    for parameterManager in parameterManagersInParameters(comp):
        parameterManager.updatePart(comp)

def previewUpdatePart(comp):
    for parameterManager in parameterManagersInParameters(comp):
        parameterManager.previewUpdatePart(comp)











# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class ModifyPart(apper.Fusion360CommandBase):
    

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):

        # selectionInput = inputs.itemById('selection_input_id')
        # selectedEntity = selectionInput.selection(0).entity
        # if selectedEntity.objectType == 'adsk::fusion::Occurrence' and selectedEntity.isReferencedComponent:
        #     selectedEntity.breakLink()
        # comp = vex_cad.getCompIfOccurrence(selectedEntity)
        # previewUpdatePart(comp)
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        ao = apper.AppObjects()
        app = adsk.core.Application.get()

        selectionInput = inputs.itemById('selection_input_id')

        selectionInput = inputs.itemById('selection_input_id')
        if selectionInput.selectionCount > 0:
            selectedEntity = selectionInput.selection(0).entity
            selectedComp = vex_cad.getCompIfOccurrence(selectedEntity)
            for i in range(3):
                if selectedComp.attributes.itemByName('vex_cad', 'part_data') and 'parameters' in vex_cad.getPartData(selectedComp):
                    if changed_input.id == 'selection_input_id':
                        showSomeCommandInputs(selectedComp)
                        if selectionInput.selectionCount == 0:
                            # ao.ui.messageBox(str(selectedEntity))
                            selectionInput.addSelection(selectedEntity)
                    else:
                        updateInputs(selectedComp)
                else:
                    selectionInput.clearSelection()
                    if selectedEntity.objectType == 'adsk::fusion::Occurrence':
                        selectedEntity = selectedEntity.assemblyContext
                        selectedComp = vex_cad.getCompIfOccurrence(selectedEntity)
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

        ao = apper.AppObjects()

        # Create a default value using a string
        default_value = adsk.core.ValueInput.createByString('1.0 in')

        # Get teh user's current units
        default_units = ao.units_manager.defaultLengthUnits


        selectionInput = inputs.addSelectionInput('selection_input_id', 'Select Parametric Part', 'Component to select')
        selectionInput.setSelectionLimits(1, 1)
        selectionInput.addSelectionFilter('Occurrences')

        createAllCommandInputs(inputs)
        hideAllCommandInputs()

        global importingPart
        global importedPart
        if importingPart:
            if importedPart.component.attributes.itemByName('vex_cad', 'part_data'):
                importedCompAttributes = vex_cad.getPartData(importedPart.component)
                if 'parameters' in importedCompAttributes:
                    selectionInput.addSelection(importedPart)
                    showSomeCommandInputs(importedPart.component)
            importingPart = False



importingPart = False
importedPart = None

class ModifyPartExternalCommandStarted(apper.Fusion360CommandEvent):

    def command_event_received(self, event_args, command_id, command_definition):
        global importingPart
        if command_id == 'FusionImportCommand':
            importingPart = True
        if command_id == 'FusionMoveCommand':
            # global importingPart
            if importingPart:
                ao = apper.AppObjects()
                tempPart = ao.ui.activeSelections.item(0).entity
                if tempPart.component.attributes.itemByName('vex_cad', 'part_data'):
                    global importedPart
                    importedPart = tempPart
                    return
                importingPart = False

class ModifyPartExternalCommandEnded(apper.Fusion360CommandEvent):

    def command_event_received(self, event_args, command_id, command_definition):
        if command_id == 'FusionMoveCommand':
            ao = apper.AppObjects()
            if importingPart:
                modify_part = ao.ui.commandDefinitions.itemById('VEX CAD_VEX CAD Library_modify_part')
                modify_part.execute()