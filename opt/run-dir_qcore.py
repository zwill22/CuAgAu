import os
import sys
import subprocess

ncpu = sys.argv[1]
time = sys.argv[2]
wd = sys.argv[3]
files = sys.argv[4]

path = os.path.abspath(wd)

queue = 'slurm'
#queue = 'pbs'

workdir = True

mem = 120
himem = False

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
#PBS -l select=1:ncpus={2}:mem={3}gb:mpiprocs={2}
""" 
        if himem:
            output += "\n#PBS -q himem"
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
        if himem:
            output += "\n#SBATCH -p hmem"
    else:
        raise ValueError("Invalid queue")

    output += """

source ${{HOME}}/.bashrc
"""

    if not workdir:
        output += """

cd {4}
tmp=${{TMPDIR}}

cp "{0}.in" ${{TMPDIR}}
cp "{0}.xyz" ${{TMPDIR}}

cd ${{TMPDIR}}
"""
    
    output += "\n\nqcore -n {2} \"{0}.in\" &> \"{0}.out\"\n"

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
