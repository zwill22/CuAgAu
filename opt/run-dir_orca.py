#!/sw/lang/anaconda.3.8-2020.07/bin/python

import os
import sys
import subprocess

ncpu = sys.argv[1]
time = sys.argv[2]
wd = sys.argv[3]
files = sys.argv[4]

path = os.path.abspath(wd)

def get_output_bp1(filename, time, ncpu, path, mem=144):
    return """#!/bin/bash -l
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
""".format(filename, time, ncpu, mem, path)


def get_output_bc4(filename, time, ncpu, path, mem):
    return """#!/bin/bash
#SBATCH -N 1
#SBATCH --tasks-per-node={0}
#SBATCH --time={1}:00:00
#SBATCH --error="%x.e%j"
#SBATCH --output="%x.o%j"
#SBATCH --jobname="{2}"

module load OpenMPI/3.0.0-GCC-7.2.0-2.29 
module load apps/orca/5.0.1
 
export RSH_COMMAND="/usr/bin/ssh -x"

cd {3}

cp "{2}.in" ${{TMPDIR}}
cp "{2}.xyz" ${{TMPDIR}}

echo ${{SLURM_NODELIST}} > ${{TMPDIR}}/{2}.nodes

cd ${{TMPDIR}}

$((which orca)) "{2}.in" &> "{2}.out"

cp "{2}.out" {3}
cp "{2}.xyz" {3}

cd {3}
""".format(ncpu, time, filename, path)
 
computer = "BC4"

if files != 'files':
    raise ValueError('only files supported')

for file in os.listdir():
    if not file.endswith('.in'):
        continue

    filename = file.split('.')[0]
    if os.path.isfile(filename + ".out"):
        continue
    
    if computer == "BP1":
        output = get_output_bp1(filename, time, ncpu, path)
    elif computer == "BC4":
        output = get_outpute_bc4(filename, time, ncpu, path)

    subfile = filename + '.sub'

    with open(subfile, 'w') as f:
        f.write(output) 
    
    if computer == "BP1":
        subprocess.run(["qsub", subfile])
    else:
        subprocess.run(["sbatch", subfile])
