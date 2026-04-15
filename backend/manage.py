#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line # type: ignore from django.core.management # type: ignore      
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and " #   type: ignore
            "available on your PYTHONPATH environment variable? Did you " # type: ignore
            "forget to activate a virtual environment?" # type: ignore
        ) from exc
    execute_from_command_line(sys.argv) # type: ignore


if __name__ == '__main__': # type: ignore
    main()
