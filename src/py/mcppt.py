import sys, os, argparse

from colors import *
from util import *

import settings
settings.update_local_status()
settings.load_settings(settings.global_settings_path, settings.s_globals)


if settings.is_local_project:
    settings.load_settings(settings.global_settings_path, settings.current)
    settings.load_settings(settings.local_settings_path, settings.current)
else:
    settings.load_settings(settings.global_settings_path, settings.current)

import commands


if __name__ == '__main__':
    print(f"{settings.is_local_project=}")

    # if no command is given:
    if len(sys.argv) < 2:
        print_error("FATAL ERROR: No command given. Valid commands are:")
        
        for cmd, desc in commands.get_command_desc().items():
            print(f"    {cmd} - {desc}")
            exit(1)

    cmd = sys.argv[1]
    cmds = commands.get_commands()

    # if command is not valid:
    if cmd not in cmds:
        print_error(f"FATAL ERROR '{cmd}' is not a valid command. Valid commands are:")
        
        for cmd, desc in commands.get_command_desc().items():
            print(f"    {cmd} - {desc}")
        sys.exit(1)
    
    # Initialize and execute command:
    cmd_runner = cmds[cmd]()
    result = cmd_runner.run(sys.argv[2:])

    if result is None:
        print_color('green', "Command completed successfully!")

        if settings.is_local_project:
            settings.save_settings(settings.local_settings_path, settings.current)            
        else:
            settings.save_settings(settings.global_settings_path, settings.current)

        sys.exit(0)
    
    elif isinstance(result, str):
        print_error(f"FATAL ERROR: {result}")
        sys.exit(1)
    
    elif isinstance(result, int):
        print_error(f"FATAL ERROR: Error code {result}")
        sys.exit(result)
    
    else:
        print_error(f"FATAL ERROR: Unknown cause - {result}")
        sys.exit(1)