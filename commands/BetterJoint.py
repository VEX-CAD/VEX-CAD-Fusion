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


# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class BetterJoint(apper.Fusion360CommandBase):

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
        # app = adsk.core.Application.get()
        # global selectedComp
        # global selectedCompAttributes


        # selectionInput = inputs.itemById('selection_input_id')

        # if changed_input.id == 'selection_input_id':
            

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Create a document.
        # doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
 
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        rootComp = design.rootComponent
        
        SelectionInput = input_values['selection_input_id']
        
        # Create the first joint geometry with the end face
        geo0 = adsk.fusion.JointGeometry.createByPoint(SelectionInput[0])
        geo1 = adsk.fusion.JointGeometry.createByPoint(SelectionInput[1])
        
        # Create joint input
        joints = rootComp.joints
        jointInput = joints.createInput(geo0, geo1)
        
        # Set the joint input
        # angle = adsk.core.ValueInput.createByString('90 deg')
        # jointInput.angle = angle
        # offset = adsk.core.ValueInput.createByString('1 cm')
        # jointInput.offset = offset
        jointInput.isFlipped = True
        jointInput.setAsRigidJointMotion()
        
        # Create the joint
        joint = joints.add(jointInput)
        
        # Get health state of a joint
        health = joint.healthState
        if health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState or health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState:
            message = joint.errorOrWarningMessage

    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        ao = AppObjects()

        # Create a default value using a string
        default_value = adsk.core.ValueInput.createByString('1.0 in')

        # Get teh user's current units
        default_units = ao.units_manager.defaultLengthUnits

        SelectionInput = inputs.addSelectionInput('selection_input_id', 'Select points on part to move', 'Points to select')
        SelectionInput.setSelectionLimits(2, 2)
        SelectionInput.addSelectionFilter('SketchPoints')

