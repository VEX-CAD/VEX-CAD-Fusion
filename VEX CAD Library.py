import os
import sys
import adsk.core
import traceback

app_path = os.path.dirname(__file__)

sys.path.insert(0, app_path)
sys.path.insert(0, os.path.join(app_path, 'apper'))

# Set to True to use beta and development features
developmentFeatures = True
unreleasedFeatures = False
# Set to True to display various useful messages when debugging
debug = False
# global addin

try:
    import config
    import apper

    from .commands.ModifyPart import ModifyPart
    from .commands.ModifyPart import FusionImportCommandStartedEvent
    from .commands.ModifyPart import FusionMoveCommandEndedEvent
    from .commands.SimpleJoint import SimpleJoint
    from .commands.SetAttributes import SetAttributes
    from .commands.ViewAttributes import ViewAttributes
    from .commands.PointsToJointOrigins import PointsToJointOrigins
    from .commands.ShowJointOriginsByBoundingBox import ShowJointOriginsByBoundingBox

    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface

    # Create addin definition object
    # global addin
    addin = apper.FusionApp(config.app_name, config.company_name, False)

    addin.add_command(
        'Modify Part',
        ModifyPart,
        {
            'cmd_description': 'Modify parametric parts from the VEX CAD Library.\n\nSelect part component and change parameters.',
            'cmd_id': 'modify_part',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'Modify',
            'cmd_resources': 'command_icons/press_pull',
            'command_visible': True,
            'command_promoted': True,
        }
    )
    # addin.commands[0].on_run()
    # addin.commands[0].on_create(adsk.core.Command, adsk.core.CommandInputs)
    # apper._CommandCreatedEventHandler(addin.commands[0])
    # _get_create_event
    # ui.commandDefinitions.itemById('Extrude').execute()
    # ui.commandDefinitions.itemById(' VEX CAD_VEX CAD Library_modify_part').execute()
    # ui.commandDefinitions.item(397).execute()
    # ui.commandDefinitions.itemById(addin.commands[0].id).execute()
    # for i in range(2200, ui.commandDefinitions.count):
    #     print(str(i) + ': ' + ui.commandDefinitions.item(i).id)

    # ui.messageBox(ui.commandDefinitions.itemById(modify_part).id)
    # ui.messageBox(str(ui.commandDefinitions))
    addin.add_command_event("FusionImportCommandStartedEvent", app.userInterface.commandStarting, FusionImportCommandStartedEvent)
    addin.add_command_event("FusionMoveCommandEndedEvent", app.userInterface.commandTerminated, FusionMoveCommandEndedEvent)

    if developmentFeatures:
        addin.add_command(
            'Set Attributes',
            SetAttributes,
            {
                'cmd_description': 'Set custom attributes for parts from the VEX CAD Library.\n\nSelect part component and input valid JSON string.',
                'cmd_id': 'set_attributes',
                'workspace': 'FusionSolidEnvironment',
                'toolbar_panel_id': 'Development',
                'cmd_resources': 'command_icons/edit',
                'command_visible': True,
                'command_promoted': True,
            }
        )

        addin.add_command(
            'View Attributes',
            ViewAttributes,
            {
                'cmd_description': 'View custom attributes for parts from the VEX CAD Library.',
                'cmd_id': 'view_attributes',
                'workspace': 'FusionSolidEnvironment',
                'toolbar_panel_id': 'Development',
                'cmd_resources': 'command_icons/attributes',
                'command_visible': True,
                'command_promoted': True,
            }
        )

    if unreleasedFeatures:
        addin.add_command(
            'Simple Joint (beta)',
            SimpleJoint,
            {
                'cmd_description': 'An easier to use joint tool for connecting VEX parts',
                'cmd_id': 'simple_joint',
                'workspace': 'FusionSolidEnvironment',
                'toolbar_panel_id': 'Assemble',
                'cmd_resources': 'command_icons/joint',
                'command_visible': True,
                'command_promoted': True,
            }
        )

        addin.add_command(
            'Points to Joint Origins',
            PointsToJointOrigins,
            {
                'cmd_description': 'Set custom attributes for parts from the VEX CAD Library.\n\nSelect part component and input valid JSON string.',
                'cmd_id': 'points_to_joint_origins',
                'workspace': 'FusionSolidEnvironment',
                'toolbar_panel_id': 'Advanced',
                'cmd_resources': 'command_icons/joint_origin',
                'command_visible': True,
                'command_promoted': True,
            }
        )

        addin.add_command(
            'Show Joint Origins by Bounding Box',
            ShowJointOriginsByBoundingBox,
            {
                'cmd_description': 'Set custom attributes for parts from the VEX CAD Library.\n\nSelect part component and input valid JSON string.',
                'cmd_id': 'show_joint_origins_by_bounding_box',
                'workspace': 'FusionSolidEnvironment',
                'toolbar_panel_id': 'Modify',
                'cmd_resources': 'command_icons/joint_origin',
                'command_visible': True,
                'command_promoted': True,
            }
        )



except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization: {}'.format(traceback.format_exc()))



def run(context):
    addin.run_app()


def stop(context):
    addin.stop_app()
    sys.path.pop(0)
    sys.path.pop(0)
