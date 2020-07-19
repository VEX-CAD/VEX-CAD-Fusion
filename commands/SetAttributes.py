import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper

# Alternatively you can import a specific function or class
from apper import AppObjects

import json, uuid

import vex_cad

# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says "pass" for any method you want to use
class SetAttributes(apper.Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        pass

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        # Get a reference to all relevant application objects in a dictionary
        ao = AppObjects()

        # selectionInput = input_values['selection_input_id']
        inputString = input_values['textBox']
        selectionInput = inputs.itemById('selection_input_id')
        
        if inputString == '':
            if selectionInput.selection(0).entity.objectType == 'adsk::fusion::Occurrence':
                entity = selectionInput.selection(0).entity.component
            else: 
                entity = selectionInput.selection(0).entity
            if entity.attributes.itemByName("vex_cad", "part_data") is not None:
                inputString = entity.attributes.itemByName("vex_cad", "part_data").value



        attributesDict = {"uuid": ''}
        try:
            attributesDict.update(json.loads(inputString))
        except:
            ao.ui.messageBox(inputString + '\n\nis not a valid JSON string.', 'Invalid entry', 
                            adsk.core.MessageBoxButtonTypes.OKButtonType, 
                            adsk.core.MessageBoxIconTypes.CriticalIconType)
            return
        
        attributesDict["uuid"] = str(uuid.uuid4())

        attributesJson = json.dumps(attributesDict)
        entity = vex_cad.getCompIfOccurrence(selectionInput.selection(0).entity)
        for index in range(entity.attributes.count):
            entity.attributes.item(index).deleteMe
        entity.attributes.add("vex_cad", "part_data", attributesJson)
        appliedAttributes = entity.attributes.itemByName("vex_cad", "part_data").value
        ao.ui.messageBox(appliedAttributes + '\n\nWas applied successfully.')


    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    # The following is a basic sample of a dialog UI

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        ao = AppObjects()

        # Create a default value using a string
        default_value = adsk.core.ValueInput.createByString('1.0 in')

        # Get teh user's current units
        default_units = ao.units_manager.defaultLengthUnits

        selectionInput = inputs.addSelectionInput('selection_input_id', 'Select Parametric Part', 'Component to select')
        selectionInput.setSelectionLimits(1, 1)
        textBox = inputs.addStringValueInput('textBox', 'JSON String')