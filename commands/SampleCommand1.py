
import adsk.core
import apper
from apper import AppObjects


class SampleCommand1(apper.Fusion360CommandBase):
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        # Create a collection of entities for move
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(extrudeFeature.bodies.item(0))

        # Create a transform to do move
        vector = adsk.core.Vector3D.create(0.0, 10.0, 0.0)
        transform = adsk.core.Matrix3D.create()
        transform.translation = vector

        # Create a move feature
        moveFeats = features.moveFeatures
        moveFeatureInput = moveFeats.createInput(bodies, transform)
        moveFeats.add(moveFeatureInput)
