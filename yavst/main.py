#!/usr/bin/env python
import sys
import os
from ConfigParser import SafeConfigParser
import subprocess


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def generate_dpf(ligand, receptor):
    try:
        print 'Creating', ligand[:-5] + 'dpf'
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
        
    run_qsub = parser.get('run', 'run_qsub')
    if run_qsub == 'True':
        run_qsub = True
    elif run_qsub == 'False':
        run_qsub = False
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

    # Copy qsubber into workspace:
    subprocess.Popen(['cp -r qsubber.py workspace/'], shell=True)

    # Copy ligands and receptor into workspace
    subprocess.Popen(['cp -r %s/* workspace/' % ligands_path], shell=True)
    subprocess.Popen(['cp -r %s workspace/' % receptor], shell=True)
    os.chdir('workspace')

    print
    pwd = subprocess.Popen(['pwd'],
        stdout=subprocess.PIPE).communicate()[0]
    print 'Working Directory:', pwd

    # If required read qsub template just ones:
    if qsub == True:
        qsub_template_file = open('../qsub_script_template', 'r')
        qsub_template = qsub_template_file.readlines()
        qsub_template_file.close()

    # Create Grid Maps for all ligands ones:
    try:
        print 'Creating Grid Parameter File'
        print
        receptor_name = receptor.split('/')[-1]
        subprocess.Popen(
            ['python', '../prepare_gpf4.py',
             '-r', receptor_name,
             '-p', 'npts=70,70,70',
             '-d', '.', ],
            stdout=subprocess.PIPE).communicate()[0]

        autogrid_run = '%s -p %s -l %s\n\n' % (
            autogrid_path,
            receptor_name[:-5] + 'gpf',
            receptor_name[:-5] + 'glg'
            )

        if qsub == True:
            # Generate qsub script:
            print 'Creating grid_generation.qsub'
            qsub_content = qsub_template + [autogrid_run]
            qsub_file = open('grid_generation', 'w')
            qsub_file.writelines(qsub_content)
            qsub_file.close()

            # Run qsub scripts:
            if run_qsub == True:
                running = subprocess.Popen(['qsub grid_generation.qsub'],
                             shell=True, stdout=subprocess.PIPE).communicate()[0]
                print running

    except:
        raise IOError('Grid Generation Failed!')


    autodock_run_list = []
    for ligand in ligand_list:
        # Generate Docking Parameter Files:
        dpf_file = generate_dpf(ligand, receptor)

        # Generate AutoDock paths:
        autodock_run = '%s -p %s -l %s\n' % (
            autodock_path, ligand[:-5] + 'dpf', ligand[:-5] + 'dlg'
            )
        autodock_run_list.append(autodock_run)

        if qsub == True:
            # Generate qsub script:
            print 'Creating', ligand[:-5] + 'qsub'
            qsub_content = qsub_template + [autodock_run]
            qsub_file = open(ligand[:-5] + 'qsub', 'w')
            qsub_file.writelines(qsub_content)
            qsub_file.close()

            # Run qsub scripts:
            if run_qsub == True:
                running = subprocess.Popen(['qsub %s.qsub' % ligand[:-5]],
                             shell=True, stdout=subprocess.PIPE).communicate()[0]
                print running
        print

    if qsub == False:
        # Generate shell script:
        print
        print 'Creating run_autodock.sh'
        run_list = [autogrid_run] + autodock_run_list
        autodock_run_list.append(run_list)
        sh_file = open('run_autodock.sh', 'w')  # This file can run by itself.
        sh_file.writelines(run_list)
        sh_file.close()
        print  # Seperate every operation.

    print "Finished!"


if __name__ == '__main__':
    main()
