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
globalInside = False

# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says 'pass' for any method you want to use
class BetterJoint(apper.Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        print('on_preview')
        if len(input_values['selection_input_id']) == 2:
            self.on_execute(command, inputs, args, input_values)
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
        print('on_input_changed')
        SelectionInput = input_values['selection_input_id']
        angle = inputs.itemById('angle_id')
        if len(SelectionInput) == 2:
            point = SelectionInput[1]
            xDirection = point.parentSketch.xDirection
            yDirection = point.parentSketch.yDirection
            angle.setManipulator(point.worldGeometry, xDirection, yDirection)
            angle.isVisible = True
            if changed_input == angle:
                # print((int(angle.value / math.tau * 4 + 0.5) % 4) * math.tau)
                # angle.value = (int(angle.value / math.tau * 4 + 0.5) % 4) * math.tau
                if angle.value > math.pi * 2 - math.pi * 0.25:
                    angle.value = math.pi * 2
                elif angle.value > math.pi * 1.5 - math.pi * 0.25:
                    angle.value = math.pi  * 1.5
                elif angle.value > math.pi * 1 - math.pi * 0.25:
                    angle.value = math.pi * 1
                elif angle.value > math.pi * 0.5 - math.pi * 0.25:
                    angle.value = math.pi * 0.5
                else:
                    angle.value = 0
        else:
            angle.isVisible = False
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
        
        # Set the joint input
        # if Rotate.listItems.item(0).isSelected:
        #     angle = vi.createByString('90 deg')
        # elif Rotate.listItems.item(1).isSelected:
        #     angle = vi.createByString('0 deg')
        # elif Rotate.listItems.item(2).isSelected:
        #     angle = vi.createByString('180 deg')
        # elif Rotate.listItems.item(3).isSelected:
        #     angle = vi.createByString('270 deg')
        # jointInput.angle = angle
        jointInput.angle = vi.createByReal(inputs.itemById('angle_id').value)
        # jointInput.angle = vi.createByReal(input_values['angle_id'])

        global globalInside
        globalInside = input_values['inside_id']
        if input_values['inside_id']:
            offset = '-0.063 in'
        else:
            offset = '0'
        jointInput.offset = vi.createByString(offset)
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

        ao = AppObjects()

        # Create a default value using a string
        default_value = adsk.core.ValueInput.createByString('1.0 in')

        # Get teh user's current units
        default_units = ao.units_manager.defaultLengthUnits

        SelectionInput = inputs.addSelectionInput('selection_input_id', 'Select points on part to move', 'Points to select')
        SelectionInput.setSelectionLimits(2, 2)
        SelectionInput.addSelectionFilter('SketchPoints')
        angle = inputs.addAngleValueCommandInput('angle_id', 'Angle', adsk.core.ValueInput.createByString('0 deg'))
        angle.isVisible = False
        # angle.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 0, 1))
        # angle.minimumValue = adsk.core.ValueInput.createByString('-360 deg')
        # angle.maximumValue = adsk.core.ValueInput.createByString('360 deg')
        # Rotate = inputs.addButtonRowCommandInput('rotate_id', 'Rotate', False)
        # Rotate.listItems.add('Left', False, 'commands/resources/rotate')
        # Rotate.listItems.add('Up', True, 'commands/resources/rotate')
        # Rotate.listItems.add('Down', False, 'commands/resources/rotate')
        # Rotate.listItems.add('Right', False, 'commands/resources/rotate')
        inputs.addBoolValueInput('flip_id', 'Flip', True, 'commands/resources/flip_allignment', globalFlip)
        inputs.addBoolValueInput('inside_id', 'Inside', True, 'commands/resources/plane_offset', globalInside)

