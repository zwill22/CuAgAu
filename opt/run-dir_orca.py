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

module load lib/openmpi
module load apps/orca
export orcadir="/sw/apps/orca/orca_4_2_0_linux_x86-64_openmpi314"
export RSH_COMMAND="/usr/bin/ssh -x"


#Setup scratch directory
cp "{0}.in" ${{TMPDIR}}
cp "{0}.xyz" ${{TMPDIR}}

# Run orca
cd ${{TMPDIR}}
export MKL_THREADING_LAYER=TBB

${{orcadir}}/orca "{0}.in" &> "{0}.out"

cp * {4}
cd {4}
""".format(filename, time, ncpu, 144, path)

    subfile = filename + '.sub'

    with open(subfile, 'w') as f:
        f.write(output) 

    subprocess.run(["qsub", subfile])
