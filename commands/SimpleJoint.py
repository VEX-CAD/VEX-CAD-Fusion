import adsk.core
import adsk.fusion
import adsk.cam

# Import the entire apper package
import apper

# Alternatively you can import a specific function or class
from apper import AppObjects

import math

globalFlip = True

# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class SimpleJoint(apper.Fusion360CommandBase):
    lastAngleValue = 0

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        if len(input_values['selection_input_id']) == 2:
            angle = inputs.itemById('angle_id')
            # if changed_input == angle:
            #     if angle.value != self.lastAngleValue:
            #         self.lastAngleValue = angle.value
            #         self.on_execute(command, inputs, args, input_values)
            # else:
            #     self.on_execute(command, inputs, args, input_values)
            self.on_execute(command, inputs, args, input_values)

            # point = SelectionInput[1]
            # point.assemblyContext.transform.setWithCoordinateSystem()
            
        # SelectionInput = input_values['selection_input_id']
        #  point = SelectionInput[1]
        # vector = adsk.core.Vector3D.create(0.0, 10.0, 0.0)
        # transform = adsk.core.Matrix3D.create()
        # transform.translation = vector
        # # Create a move feature
        # moveFeats = features.moveFeatures
        # moveFeatureInput = moveFeats.createInput(bodies, transform)
        # moveFeats.add(moveFeatureInput)
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        ao = AppObjects()
        SelectionInput = input_values['selection_input_id']
        angle = inputs.itemById('angle_id')
        if len(SelectionInput) == 2:
            point = SelectionInput[1]
            # ao.ui.messageBox(str(point))
            # ao.ui.messageBox(str(point.assemblyContext.name))

            xDirection = point.parentSketch.xDirection
            yDirection = point.parentSketch.yDirection
            angle.setManipulator(point.worldGeometry, xDirection, yDirection)
            angle.isVisible = True
            if changed_input == angle:                
                for multiplier in range(8, -1, -1):
                    if angle.value > math.pi * multiplier / 4 - math.pi / 8:
                        angle.value = math.pi * multiplier / 4
                        break
        else:
            angle.isVisible = False
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

        # Get the root component of the active design
        rootComp = design.rootComponent
        
        SelectionInput = input_values['selection_input_id']
        Rotate = inputs.itemById('rotate_id')
        
        # Create the first joint geometry with the end face
        geo0 = adsk.fusion.JointGeometry.createByPoint(SelectionInput[0])
        geo1 = adsk.fusion.JointGeometry.createByPoint(SelectionInput[1])
        
        # Create joint input
        joints = rootComp.joints
        jointInput = joints.createInput(geo0, geo1)
        
        jointInput.angle = vi.createByReal(inputs.itemById('angle_id').value)
        global globalFlip
        globalFlip = input_values['flip_id']
        jointInput.isFlipped = input_values['flip_id']
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

        SelectionInput = inputs.addSelectionInput('selection_input_id', 'Points', 'Select a sketch point to place the Joint Origin')
        SelectionInput.setSelectionLimits(2, 2)
        SelectionInput.addSelectionFilter('SketchPoints')
        angle = inputs.addAngleValueCommandInput('angle_id', 'Angle', adsk.core.ValueInput.createByString('0 deg'))
        angle.isVisible = False
        inputs.addBoolValueInput('flip_id', 'Flip', True, 'commands/resources/command_icons/flip_allignment', globalFlip)

