# apps/core/management/commands/runserver.py
from django.core.management.commands.runserver import Command as RunserverCommand
from django.conf import settings
from django.core.management import call_command
import os

class Command(RunserverCommand):
    help = 'Starts a lightweight Web server for development and shows available URLs.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
    def handle(self, *args, **options):
        # First, show the startup info
        call_command('print_startup_info')
        
        # Then run the original runserver command
        super().handle(*args, **options)