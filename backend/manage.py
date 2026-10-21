#!/usr/bin/env python
import os
import sys


# This function serves to execute administrative tasks for the Django backend.
def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Could not import Django on this machine.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()