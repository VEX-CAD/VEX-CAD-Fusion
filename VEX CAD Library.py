import os
import sys
import adsk.core
import traceback

app_path = os.path.dirname(__file__)

sys.path.insert(0, app_path)
sys.path.insert(0, os.path.join(app_path, 'apper'))

try:
    import config
    import apper

    from .commands.ModifyPart import ModifyPart
    from .commands.SimpleJoint import SimpleJoint
    from .commands.SetAttributes import SetAttributes
    from .commands.ViewAttributes import ViewAttributes

# Create addin definition object
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

    addin.add_command(
        'Simple Joint',
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
        'Set Attributes',
        SetAttributes,
        {
            'cmd_description': 'Set custom attributes for parts from the VEX CAD Library.\n\nSelect part component and input valid JSON string.',
            'cmd_id': 'set_attributes',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'Advanced',
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
            'toolbar_panel_id': 'Advanced',
            'cmd_resources': 'command_icons/attributes',
            'command_visible': True,
            'command_promoted': True,
        }
    )

    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface

except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization: {}'.format(traceback.format_exc()))

# Set to True to display various useful messages when debugging your app
debug = False


def run(context):
    addin.run_app()


def stop(context):
    addin.stop_app()
    sys.path.pop(0)
    sys.path.pop(0)
