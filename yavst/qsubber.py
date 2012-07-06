import subprocess
import os

# Qsub Files:
qsub_list = subprocess.Popen(
    ['ls -1 *.qsub'], shell=True,
    stdout=subprocess.PIPE).communicate()[0]
qsub_list = qsub_list.split('\n')[:-1]  # Last item is empty!

for item in qsub_list:
    qsubbing = subprocess.Popen(
        ['qsub %s' % item], shell=True,
        stdout=subprocess.PIPE).communicate()[0]
    print qsubbing
