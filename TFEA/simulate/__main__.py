#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
'''This runs the simulate subpackage within TFEA.
'''
#==============================================================================
__author__ = 'Jonathan D. Rubin and Rutendo F. Sigauke'
__credits__ = ['Jonathan D. Rubin', 'Rutendo F. Sigauke', 'Jacob T. Stanley',
                'Robin D. Dowell']
__maintainer__ = 'Jonathan D. Rubin'
__email__ = 'Jonathan.Rubin@colorado.edu'
__version__ = '4.0'

#Imports
#==============================================================================
import sys
from pathlib import Path
# Add TFEA srcdirectory into path
srcdirectory = Path(__file__).absolute().parent
sys.path.insert(0, srcdirectory.parent)

from TFEA.simulate import main

main.run()