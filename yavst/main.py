#!/usr/bin/env python
import sys
import os
from ConfigParser import SafeConfigParser
import subprocess


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def generate_gpf(ligand, receptor):
    try:
        print "Creating", ligand[:-5] + 'gpf'
        subprocess.Popen(
            ['python', '../prepare_gpf4.py',
             '-l', ligand,
             '-r', receptor.split('/')[-1],
             '-p', 'npts=60,60,60',
             '-o', ligand[:-5] + 'gpf', ],
            stdout=subprocess.PIPE).communicate()[0]
        return True
    except:
        return False


def generate_dpf(ligand, receptor):
    try:
        print "Creating", ligand[:-5] + 'dpf'
        subprocess.Popen(
            ['python', '../prepare_dpf4.py',
             '-l', ligand,
             '-r', receptor.split('/')[-1],
             '-p', 'ga_num_evals=20000000',
             '-p', 'ga_pop_size=150',
             '-p', 'ga_run=10',
             '-o', ligand[:-5] + 'dpf', ],
            stdout=subprocess.PIPE).communicate()[0]
        return True
    except:
        return False


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

    autogrid_path = parser.get('run', 'autogrid')
    autodock_path = parser.get('run', 'autodock')

    qsub = parser.get('run', 'qsub')
    if qsub == 'True':
        qsub = True
    elif qsub == 'False':
        qsub = False
    else:
        raise IOError('Wrong qsub option! (True/False)')
        
    running = parser.get('run', 'running')
    if running == 'True':
        running = True
    elif running == 'False':
        running = False
    else:
        raise IOError('Wrong running option! (True/False)')

    # Ligand path should include a slash at the end:
    if ligands[-1] == '/':
        ligands_path = ligands
    else:
        ligands_path = ligands + '/'

    # Ligand List:
    ligand_list = subprocess.Popen(
        ['ls', '-1', ligands_path],
        stdout=subprocess.PIPE).communicate()[0]
    ligand_list = ligand_list.split('\n')[:-1]  # Last item is empty!

    # Create griding and docking workspace:
    subprocess.Popen(['mkdir', 'workspace'],
                     stdout=subprocess.PIPE).communicate()[0]

    # Copy ligands and receptor into workspace
    subprocess.Popen(['cp -r %s/* workspace/' % ligands_path], shell=True)
    subprocess.Popen(['cp -r %s workspace/' % receptor], shell=True)
    os.chdir('workspace')

    pwd = subprocess.Popen(['pwd'],
        stdout=subprocess.PIPE).communicate()[0]
    print pwd

    gpf_list = []  # holds all gpf files in workspace
    dpf_list = []  # holds all dpf files in workspace
    qsub_list = []  # holds all qsub scripts in workspace

    # If required read qsub template just ones:
    if qsub == True:
        qsub_template_file = open('../qsub_script_template', 'r')
        qsub_template = qsub_template_file.readlines()
        qsub_template_file.close()

    for ligand in ligand_list:
        # Generate Grid Parameter Files for every ligand
        gpf_file = generate_gpf(ligand, receptor)
        gpf_list.append(gpf_file)

        # Generate Docking Parameter Files:
        dpf_file = generate_dpf(ligand, receptor)
        dpf_list.append(dpf_file)

        # Generate running paths:
        autogrid = '%s -p %s -l %s\n' % (
            autogrid_path, ligand[:-5] + 'gpf', ligand[:-5] + 'glg'
            )
        autodock = '%s -p %s -l %s\n' % (
            autodock_path, ligand[:-5] + 'dpf', ligand[:-5] + 'dlg'
            )


        if qsub == True:
            # Generate qsub script:
            print "Creating", ligand[:-5] + 'qsub'
            qsub_content = qsub_template + [autogrid, autodock]
            qsub_file = open(ligand[:-5] + 'qsub', 'w')
            qsub_file.writelines(qsub_content)
            qsub_file.close()

            # Run qsub scripts:
            if running == True:
                run_qsub = subprocess.Popen(['qsub', ligand[:-5] + 'qsub'],
                                  stdout=subprocess.PIPE).communicate()[0]
                print run_qsub

        else:
            # Generate shell script:
            print "Creating", ligand[:-5] + 'sh'
            sh_content = [autogrid, autodock]
            sh_file = open(ligand[:-5] + 'sh', 'w')
            sh_file.writelines(sh_content)
            sh_file.close()

            # Run sh scripts:
            if running == True:
                run_sh = subprocess.Popen(['sh', ligand[:-5] + 'sh'],
                                  stdout=subprocess.PIPE).communicate()[0]
                print run_sh

        print  # Seperate every operation.

    print "Finished!"


if __name__ == '__main__':
    main()
