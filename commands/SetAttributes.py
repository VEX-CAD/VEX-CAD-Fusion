import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper

# Alternatively you can import a specific function or class
from apper import AppObjects

import json


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
        # # Selections are returned as a list so lets get the first one
        # all_selections = input_values.get('selection_input_id', None)

        # if all_selections is not None:
        #     the_first_selection = all_selections[0]

        #     # Update the text of the string value input to show the type of object selected
        #     text_box_input = inputs.itemById('text_box_input_id')
        #     text_box_input.text = the_first_selection.objectType

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):

        # Get the values from the user input
        # the_value = input_values['value_input_id']
        # the_boolean = input_values['bool_input_id']
        # the_string = input_values['string_input_id']
        # all_selections = input_values['selection_input_id']
        # the_drop_down = input_values['drop_down_input_id']

        # Selections are returned as a list so lets get the first one and its name
        # the_first_selection = all_selections[0]
        # the_selection_type = the_first_selection.objectType

        selectionInput = input_values['selection_input_id']
        # if selectionInput.selection(0).entity == app.activeProduct.rootComponent:
        selectedComp = selectionInput[0]
        jsonString = input_values['textBox']

        # Get a reference to all relevant application objects in a dictionary
        ao = AppObjects()

        # textBox = inputs.itemById('textBox')
        selectionInput = inputs.itemById('selection_input_id')
        if selectionInput.selectionCount > 0:
            # textBox.isVisible = True
            if selectionInput.selection(0).entity.objectType == 'adsk::fusion::Occurrence':
                entity = selectionInput.selection(0).entity.component
            else: 
                entity = selectionInput.selection(0).entity
            if entity.attributes.count > 0:
                try:
                    json.loads(jsonString)
                    entity.attributes.add("VFL", "partData", jsonString)
                    appliedAttributes = entity.attributes.itemByName("VFL", "partData").value
                    ao.ui.messageBox(appliedAttributes + '\n\nWas applied successfully.')
                except:
                    ao.ui.messageBox(jsonString + '\n\nis not a valid JSON string.', 'Invalid entry', 
                                    adsk.core.MessageBoxButtonTypes.OKButtonType, 
                                    adsk.core.MessageBoxIconTypes.CriticalIconType)
            else:
                ao.ui.messageBox('The selection does not have any attributes')


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
        selectionInput.setSelectionLimits(1, 0)
        textBox = inputs.addStringValueInput('textBox', 'JSON String')