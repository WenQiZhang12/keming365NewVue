#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run inspectdb and output to a file."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
django.setup()

from django.core.management import call_command

output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', '_generated_models.py')

with open(output_file, 'w', encoding='utf-8') as f:
    call_command('inspectdb', database='default', stdout=f)

print(f"Models generated and saved to: {output_file}")
