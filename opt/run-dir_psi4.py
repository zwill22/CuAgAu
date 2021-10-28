#!/sw/lang/anaconda.3.8-2020.07/bin/python

import os
import sys
import subprocess

ncpu = sys.argv[1]
time = sys.argv[2]
wd = sys.argv[3]
files = sys.argv[4]

path = os.path.abspath(wd)

if files != 'files':
    raise ValueError('only files supported')

for file in os.listdir():
    if not file.endswith('.in'):
        continue

    filename = file.split('.')[0]
    if os.path.isfile(filename + ".out"):
        continue
   
    output = """#!/bin/bash -l
#PBS -N "{0}"
#PBS -j oe
#PBS -l walltime={1}:00:00
#PBS -l select=1:ncpus={2}:mem={3}gb:mpiprocs={2}

cd {4}

source /home/zw18965/.bashrc

tmp=${{TMPDIR}}
export MKL_THREADING_LAYER=""

conda activate p4env

cp "{0}.in" ${{TMPDIR}}
cp "{0}.xyz" ${{TMPDIR}}

cd ${{TMPDIR}}

psi4 -n {2} -i "{0}.in" &> "{0}.out"

cp {0}* {4}
cd {4}
""".format(filename, time, ncpu, 144, path)

    subfile = filename + '.sub'

    with open(subfile, 'w') as f:
        f.write(output) 

    subprocess.run(["qsub", subfile])
