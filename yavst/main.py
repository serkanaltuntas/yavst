#!/usr/bin/env python
import sys
import os
from ConfigParser import SafeConfigParser


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def main():
    # Read inputs:
    try:
        inputfile = str(sys.argv[1])
    except:
        raise IOError('Please specify an input file!')

    parser = SafeConfigParser()
    parser.read(os.path.join(PROJECT_ROOT, inputfile))

    receptor = parser.get('molecules', 'receptor')
    ligands = parser.get('molecules', 'ligands')
    center = parser.get('gridbox', 'center')
    box = parser.get('gridbox', 'box')

    # Ligand path should include a slash at the end:
    if ligands[-1] == '/': ligands_path = ligands
    else: ligands_path = ligands + '/'

    # Generate Grid Parameter Files:
    # Generate Docking Parameter Files:
    # Generate qsub scripts:
    # Run qsub scripts:
    print "Finished!"


if __name__ == '__main__':
    main()
