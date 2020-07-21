import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper
# import config

# Alternatively you can import a specific function or class
# from apper import apper.AppObjects

import json

import vex_cad

allParameterManagers = []

def defineParameterManagers():
    ao = apper.AppObjects()
    unitsMgr = ao.units_manager

    coordSys = {'origin': 0, 'xAxis': 1, 'yAxis': 2, 'zAxis': 3}

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


    class ParameterManager:
        def __init__(self, id, name):
            self.id = id
            self.name = name
            self.parameterId = id
        # Defaults
        def hide(self):
            self.commandInput.isVisible = False
        def onUpdate(self, occ):
            pass
        def previewUpdatePart(self, occ):
            comp = occ.component
            self.updatePart(occ)

        # Need to be redefined
        def create(self, commandInputs):
            pass
        def show(self, occ):
            pass
        def onUpdate(self, occ, changedInput):
            pass
    
    class ButtonRowInserts(ParameterManager):
        def create(self, commandInputs):
            self.commandInput = commandInputs.addButtonRowCommandInput(self.id, self.name, False)
        
        def show(self, occ):
            comp = occ.component
            self.commandInput.listItems.clear()
            isSquareSelected = iSInsertVisible(comp, 'square')
            isRoundSelected = iSInsertVisible(comp, 'round')
            self.commandInput.listItems.add('None', not isRoundSelected and not isSquareSelected, 'commands/resources/command_icons/insert_none')
            self.commandInput.listItems.add('Square', isSquareSelected, 'commands/resources/command_icons/insert_square')
            self.commandInput.listItems.add('Round', isRoundSelected, 'commands/resources/command_icons/insert_round')
            self.commandInput.isVisible = True

        def updatePart(self, occ):
            comp = occ.component
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
    
    class DistanceModule(ParameterManager):
        def create(self, commandInputs):
            self.commandInput = commandInputs.addDistanceValueCommandInput(self.id, self.name, adsk.core.ValueInput.createByReal(0))
        
        def show(self, occ):
            comp = occ.component
            ao = apper.AppObjects()
            parameter = vex_cad.getPartData(comp)['parameters'][self.parameterId]
            
            self.commandInput.expression = comp.modelParameters.item(parameter['index']).expression
            self.commandInput.minimumValue = parameter['min_value']
            self.commandInput.maximumValue = parameter['max_value']
            
            occMatrix3D = occ.transform
            if 'manipulator_point_offset' in parameter:
                pointOffset = parameter['manipulator_point_offset']
                newMatrix3D = adsk.core.Matrix3D.create()
                for i in range(3):
                    newMatrix3D.setCell(i, 3, pointOffset[i])
                newMatrix3D.transformBy(occMatrix3D)
                occMatrix3DCoords = newMatrix3D.getAsCoordinateSystem()
            else:
                occMatrix3DCoords = occMatrix3D.getAsCoordinateSystem()
            
            occVector3D = occMatrix3DCoords[coordSys[parameter['manipulator_axis']]]
            if 'manipulator_axis_flipped' in parameter and parameter['manipulator_axis_flipped']:
                occVector3D.scaleBy(-1)
            occPoint3D = occMatrix3DCoords[coordSys['origin']]
            self.commandInput.setManipulator(occPoint3D, occVector3D)
            self.commandInput.isVisible = True

        def updatePart(self, occ):
            comp = occ.component
            parameter = vex_cad.getPartData(comp)['parameters'][self.parameterId]
            ao = apper.AppObjects()
            unitsMgr = ao.units_manager
            if unitsMgr.isValidExpression(self.commandInput.expression, ''):
                comp.modelParameters.item(parameter['index']).value = self.commandInput.value

    class DistanceGroup(ParameterManager):
        def create(self, commandInputs):
            self.group = commandInputs.addGroupCommandInput(self.id, self.name)
            self.distanceValue = DistanceModule(self.id + '_distance_value', 'Distance')
            self.distanceValue.create(self.group.children)
            self.distanceValue.parameterId = self.id

        def show(self, occ):
            self.distanceValue.show(occ)
            self.group.isVisible = True

        def hide(self):
            self.distanceValue.hide()
            self.group.isVisible = False

        def updatePart(self, occ):
            self.distanceValue.updatePart(occ)

    class DistanceSliderHoles(ParameterManager):
        def create(self, commandInputs):
            self.group = commandInputs.addGroupCommandInput(self.id, self.name)
            self.intSlider = self.group.children.addIntegerSliderCommandInput(self.id + '_int_slider', 'Holes', 0, 40)
            self.distanceValue = DistanceModule(self.id + '_distance_value', 'Distance')
            self.distanceValue.create(self.group.children)
            self.distanceValue.parameterId = self.id

        def show(self, occ):
            comp = occ.component
            parameter = vex_cad.getPartData(comp)['parameters'][self.parameterId]
            self.distanceValue.show(occ)
            self.intSlider.minimumValue = int(parameter['min_value'] / 1.27)
            self.intSlider.maximumValue = int(parameter['max_value'] / 1.27)
            if self.distanceValue.commandInput.isValidExpression:
                self.intSlider.valueOne = int(self.distanceValue.commandInput.value / 1.27 + 0.99)
            self.intSlider.isVisible = True
            self.group.isVisible = True

        def hide(self):
            self.distanceValue.hide()
            self.intSlider.isVisible = False
            self.group.isVisible = False

        def onUpdate(self, occ, changedInput):
            comp = occ.component
            if  changedInput == self.distanceValue.commandInput:
                if self.distanceValue.commandInput.isValidExpression:
                    self.intSlider.valueOne = int(self.distanceValue.commandInput.value / 1.27 + 0.99)
                
            else:
                self.distanceValue.commandInput.value = self.intSlider.valueOne * 1.27

        def updatePart(self, occ):
            self.distanceValue.updatePart(occ)

    class DistanceDropDown(ParameterManager):
        def create(self, commandInputs):
            self.group = commandInputs.addGroupCommandInput(self.id, self.name)
            self.dropDownInput = self.group.children.addDropDownCommandInput(self.id + '_options', 'Standard Sizes', 1)
            self.distanceValue = DistanceModule(self.id + '_distance_value', 'Distance')
            self.distanceValue.create(self.group.children)
            self.distanceValue.parameterId = self.id

        def show(self, occ):
            comp = occ.component
            parameter = vex_cad.getPartData(comp)['parameters'][self.parameterId]
            self.distanceValue.show(occ)
            self.dropDownInput.listItems.clear()
            self.dropDownInput.listItems.add('Custom', True)
            parameter = vex_cad.getPartData(comp)['parameters'][self.parameterId]
            for item in parameter["expressions"]:
                isSelected = comp.modelParameters.item(parameter['index']).value == unitsMgr.evaluateExpression(item, '')
                self.dropDownInput.listItems.add(item, isSelected)
            
            self.dropDownInput.isVisible = True
            self.distanceValue.isVisible = True
            self.group.isVisible = True

        def hide(self):
            self.distanceValue.hide()
            self.dropDownInput.isVisible = False
            self.group.isVisible = False

        def onUpdate(self, occ, changedInput):
            comp = occ.component
            selectedName = self.dropDownInput.selectedItem.name
            if  changedInput == self.distanceValue.commandInput:
                ao = apper.AppObjects()
                unitsMgr = ao.units_manager
                self.dropDownInput.listItems.item(0).isSelected = True
            elif  selectedName != 'Custom':
                self.distanceValue.commandInput.expression = selectedName

        def updatePart(self, occ):
            self.distanceValue.updatePart(occ)
    
    return [
        ButtonRowInserts('inserts_v1', 'Inserts'),
        DistanceGroup('distance_length_v1', 'Length'),
        DistanceDropDown('distance_list_size_v1', 'Size'),
        DistanceSliderHoles('distance_holes_length_v1', 'Length'),
        DistanceSliderHoles('distance_holes_width_v1', 'Width')
    ]


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

def showSomeCommandInputs(occ):
    for parameterManager in parameterManagersInParameters(occ.component):
        parameterManager.show(occ)

def updateInputs(occ, changedInput):
    for parameterManager in parameterManagersInParameters(occ.component):
        parameterManager.onUpdate(occ, changedInput)

def updatePart(occ):
    for parameterManager in parameterManagersInParameters(occ.component):
        parameterManager.updatePart(occ)

def previewUpdatePart(occ):
    for parameterManager in parameterManagersInParameters(occ.component):
        parameterManager.previewUpdatePart(occ)











# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class ModifyPart(apper.Fusion360CommandBase):
    

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):

        selectionInput = inputs.itemById('selection_input_id')
        selectedOcc = selectionInput.selection(0).entity
        if selectedOcc.isReferencedComponent:
            return
        compFaces = 0
        for i in range(selectedOcc.component.bRepBodies.count):
            compFaces = compFaces + selectedOcc.component.bRepBodies.item(i).faces.count
        if compFaces > 300:
            return
        previewUpdatePart(selectedOcc)

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
        if selectionInput.selectionCount > 0:
            selectedOcc = selectionInput.selection(0).entity
            # Prevent the root component from being selected
            if selectedOcc.objectType != 'adsk::fusion::Occurrence':
                selectionInput.clearSelection()
                return
            selectedComp = selectedOcc.component
            # Check if the part is parametric, if not check it's parent occurrence
            for i in range(2):
                if selectedComp.attributes.itemByName('vex_cad', 'part_data') and 'parameters' in vex_cad.getPartData(selectedComp):
                    if changed_input.id == 'selection_input_id':
                        # This is needed if the user selects a differant part without deselecting first
                        hideAllCommandInputs()
                        # Show the the controls for the parameters the part has
                        showSomeCommandInputs(selectedOcc)
                        if selectionInput.selectionCount == 0:
                            selectionInput.addSelection(selectedOcc)
                    else:
                        # ao.ui.messageBox('before updateInputs: ' + str(selectedOcc))
                        updateInputs(selectedOcc, changed_input)
                else:
                    selectionInput.clearSelection()
                    # If the selected part is an occurrence and has a parent occurrence
                    if '+' in selectedOcc.fullPathName:
                        # Get the sellected part's parent Occurrence
                        selectedOcc = selectedOcc.assemblyContext
                        selectedComp = selectedOcc.component
        else:
            # Hide the commands for the parameters from the last selected part
            hideAllCommandInputs()

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        selectionInput = inputs.itemById('selection_input_id')
        selectedOcc = selectionInput.selection(0).entity
        if selectedOcc.isReferencedComponent:
            selectedOcc.breakLink()
        updatePart(selectedOcc)

    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        ao = apper.AppObjects()

        selectionInput = inputs.addSelectionInput('selection_input_id', 'Part', 'Component to select')
        selectionInput.setSelectionLimits(1, 1)
        selectionInput.addSelectionFilter('Occurrences')

        createAllCommandInputs(inputs)
        hideAllCommandInputs()

        global importingPart
        global importedPart
        if importingPart:
            # if importedPart.attributes.itemByName('vex_cad', 'part_data'):
            # importedCompAttributes = vex_cad.getPartData(importedPart)
            # if 'parameters' in importedCompAttributes:
            selectionInput.addSelection(importedPart)
            showSomeCommandInputs(importedPart)
            importingPart = False

importingPart = False
importedPart = None

class ModifyPartExternalCommandStarted(apper.Fusion360CommandEvent):

    def command_event_received(self, event_args, command_id, command_definition):
        global importingPart
        if command_id == 'FusionImportCommand':
            importingPart = True
        if command_id == 'FusionMoveCommand':
            if importingPart:
                ao = apper.AppObjects()
                tempPart = ao.ui.activeSelections.item(0).entity
                if tempPart.component.attributes.itemByName('vex_cad', 'part_data') and 'parameters' in vex_cad.getPartData(tempPart.component):
                    global importedPart
                    importedPart = tempPart
                else:
                    importingPart = False

class ModifyPartExternalCommandEnded(apper.Fusion360CommandEvent):

    def command_event_received(self, event_args, command_id, command_definition):
        if command_id == 'FusionMoveCommand':
            ao = apper.AppObjects()
            if importingPart:
                modify_part = ao.ui.commandDefinitions.itemById('VEX CAD_VEX CAD Library_modify_part')
                modify_part.execute()