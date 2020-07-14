import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper

# Alternatively you can import a specific function or class
from apper import AppObjects

import math

allInputObjects = []

selectedComp = None
selectedCompAttributes = None

globalFlip = True

# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class ShowJointOriginsByBoundingBox(apper.Fusion360CommandBase):
    lastAngleValue = 0

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
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Create a document.
        # doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
 
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        vi = adsk.core.ValueInput
        
        selectionInput = inputs.itemById('selection_input_id')
        if selectionInput.selection(0).entity.objectType == 'adsk::fusion::Occurrence':
            comp = selectionInput.selection(0).entity.component
        else: 
            comp = selectionInput.selection(0).entity
        for jointOrigin in comp.allJointOrigins:
            # ui.messageBox(jointOrigin.name)
            # isInside = comp.boundingBox.contains(jointOrigin.geometry.origin)
            # ui.messageBox(comp.bRepBodies.itemByName('main').name)
            box = comp.bRepBodies.itemByName('main').boundingBox
            # box.expand(jointOrigin.geometry.origin)
            isInside = box.contains(jointOrigin.geometry.origin)
            # ui.messageBox(str(isInside))
            jointOrigin.timelineObject.isSuppressed = not isInside
            # jointOrigin.isLightBulbOn = isInside
        

    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        selectionInput = inputs.addSelectionInput('selection_input_id', 'Component', 'Select Component')
        selectionInput.setSelectionLimits(1, 1)
        selectionInput.addSelectionFilter('Occurrences')

