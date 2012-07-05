#!/usr/bin/env python
import sys
import os
from ConfigParser import SafeConfigParser
import subprocess


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def generate_gpf(ligand, receptor):
    print "Creating", ligand[:-5]+'gpf'
    subprocess.Popen(
        ['python', '../prepare_gpf4.py',
         '-l', ligand,
         '-r', receptor.split('/')[-1],
         '-p', 'npts=60,60,60',
         '-o', ligand[:-5]+'gpf',],
        stdout=subprocess.PIPE).communicate()[0]
    return True


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

    # Ligand List:
    ligand_list = subprocess.Popen(
        ['ls', '-1', ligands_path],
        stdout=subprocess.PIPE).communicate()[0]
    ligand_list = ligand_list.split('\n')[:-1]  # Last item is empty!

    # Create griding and docking workspace:
    subprocess.Popen(['mkdir', 'workspace'], stdout=subprocess.PIPE).communicate()[0]

    # Copy ligands and receptor into workspace
    subprocess.Popen(['cp -r %s/* workspace/' % ligands_path], shell=True)
    subprocess.Popen(['cp -r %s workspace/' % receptor], shell=True)
    os.chdir('workspace')

    pwd = subprocess.Popen(['pwd'],
        stdout=subprocess.PIPE).communicate()[0]
    print pwd

    # Generate Grid Parameter Files for every ligand
    gpf_list = []
    for ligand in ligand_list:
        gpf_file = generate_gpf(ligand, receptor)
        gpf_list.append(gpf_file)
    # gpf_list holds all gpf files in workspace

    # Generate Docking Parameter Files:
    # Generate qsub scripts:
    # Run qsub scripts:
    print "Finished!"


if __name__ == '__main__':
    main()
