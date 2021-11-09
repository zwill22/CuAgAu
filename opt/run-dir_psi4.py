import os
import sys
import subprocess

ncpu = sys.argv[1]
time = sys.argv[2]
wd = sys.argv[3]
files = sys.argv[4]

path = os.path.abspath(wd)
himem = False

hostname = os.uname().nodename
if "newblue" in hostname:
    queue = 'pbs'
    mem = 240 if himem else 64
    workdir = True
elif 'bc4' in hostname:
    queue = 'slurm'
    mem = 480 if himem else 120
    workdir = True
elif 'bp1' in hostname:
    queue = 'slurm'
    mem = 320 if himem else 150
    workdir = False
else:
    raise ValueError("Unable to determine identity of host computer")


if files != 'files':
    raise ValueError('only files supported')

for file in os.listdir():
    if not file.endswith('.in'):
        continue

    filename = file.split('.')[0]
    if os.path.isfile(filename + ".out"):
        continue
    
    if queue == 'pbs':
        output = """#!/bin/bash -l
#PBS -N "{0}"
#PBS -j oe
#PBS -l walltime={1}:00:00
#PBS -l select=1:ncpus={2}:mem={3}gb
""" 
    elif queue == 'slurm':
        output = """#!/bin/bash -l
#SBATCH -N 1
#SBATCH --tasks-per-node={2}
#SBATCH --time={1}:00:00
#SBATCH --job-name="{0}"
#SBATCH --error="{0}.e%j"
#SBATCH --output="{0}.o%j"
#SBATCH --mem={3}G
"""
    else:
        raise ValueError("Invalid queue")

    output += """

source ${{HOME}}/.bashrc
export MKL_THREADING_LAYER=""
conda activate p4env

cd {4}
"""

    if not workdir:
        output += """
tmp=${{TMPDIR}}

cp "{0}.in" $tmp
cp "{0}.xyz" $tmp

cd $tmp
"""
    
    output += "\n\npsi4 -n {2} -i \"{0}.in\" -o \"{0}.out\"\n"

    if not workdir:
        output += "\ncp {0}* {4}\ncd {4}\n"

    output = output.format(filename, time, ncpu, mem, path)

    subfile = filename + '.sub'

    with open(subfile, 'w') as f:
        f.write(output) 
    
    if queue == 'pbs':
        subprocess.run(["qsub", subfile])
    elif queue == 'slurm':
        subprocess.run(["sbatch", subfile])
    else:
        raise ValueError("Invalid queue")
