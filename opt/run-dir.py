import os
import subprocess


def get_header(system, queue, *args):
    if system == 'pbs':
        output = """#!/bin/bash -l
#PBS -N "{0}"
#PBS -j oe
#PBS -l walltime={1}
#PBS -l select={2}:ncpus={3}:mem={4}gb:mpiprocs={3}
""" 
        if queue not in ("default", "plong"):
            output += "#PBS -q {}".format(queue)
    elif system == 'slurm':
        output = """#!/bin/bash -l
#SBATCH -N {2}
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task={3}
#SBATCH --time={1}
#SBATCH --job-name="{0}"
#SBATCH --error="{0}.e%j"
#SBATCH --output="{0}.o%j
#SBATCH --mem={4}G
"""
        if queue not in ("default", "plong"):
            output += "#SBATCH -p {}".format(queue)
    else:
        raise ValueError("Invalid queuing system: {}".format(system))
    
    output += """

source ${{HOME}}/.bashrc

cd {5}
"""

    return output.format(*args)


def get_host_specs(hostname, queue, ncpu):
    if ncpu < 0:
        raise ValueError("Number of cpus cannot be negative")

    if "newblue" in hostname:
        system = 'pbs'
        if ncpu > 16:
            raise ValueError("Too many cpus ({} > 16) for BC3".format(ncpu))
        if queue == "himem":
            mem = 240
        elif queue == "default":
            mem = 64
        else:
            raise ValueError("Invalid queue for BC3: {}".format(queue))
        workdir = True
    elif 'bc4' in hostname:
        system = 'slurm'
        if ncpu > 28:
            raise ValueError("Too many cpus ({} > 28) for BC4".format(ncpu))
        if queue == "himem":
            mem = 480
        elif queue == "default":
            mem = 120
        else:
            raise ValueError("Invalid queue for BC4: {}".format(queue))
        workdir = True
    elif 'bp1' in hostname:
        system = 'slurm'
        if queue == "amd":
            mem = 950
            if ncpu > 120:
                raise ValueError("Too many cpus for BP1 (amd): {} > 120".format(ncpu))
        elif queue == "highmem":
            mem = 720
            if ncpu > 8:
                raise ValueError("Too many cpus for BP1 (highmem): {} > 8".format(ncpu))
        elif queue == "plong":
            mem = 350
            if ncpu > 32:
                raise ValueError("Too many cpus for BP1 (plong): {} > 32".format(ncpu))
        elif queue == "default":
            mem = 150
            if ncpu > 32:
                raise ValueError("Too many cpus for BP1: {} > 32".format(ncpu))
        else: 
            raise ValueError("Invalid queue for BP1: {}".format(queue))
        workdir = False
    else:
        raise ValueError("Unable to determine identity of host computer")

    return system, mem, workdir
 

def generate_program_input(prog, *args, export=True):
    output = "\n\n"
    if prog == "qcore":
        output += "qcore -n {3} \"{0}.in\" &> \"{0}.out\""
    elif prog == "orca":
        output += "$((which orca)) \"{0}.in\" &> \"{0}.out\""
    elif prog == "psi4":
        if export:
            output += "export MKL_THREADING_LAYER=\"\"\n\n"
        output += "psi4 -n {3} -i \"{0}.in\" -o \"{0}.out\""
    else:
        raise ValueError("Unrecognised program: {}".format(prog)) 
    output += "\n"

    return output.format(*args)


def generate_file_output(filename, system, queue, workdir, prog, *args):
    output = get_header(system, queue, filename, *args)
    
    if not workdir:
        output += """

tmp=${{TMPDIR}}

cp "{0}.in" $tmp
cp "{0}.xyz" $tmp

cd $tmp
""".format(filename)
    
    output += generate_program_input(prog, filename, *args)

    if not workdir:
        output += "\ncp {0}* {4}\ncd {4}\n".format(filename, *args)

    return output


def write_file(output, subfile):
    with open(subfile, 'w') as f:
        f.write(output) 
    

def submit_file(subfile, system):
    if queue == 'pbs':
        subprocess.run(["qsub", subfile])
    elif queue == 'slurm':
        subprocess.run(["sbatch", subfile])
    else:
        raise ValueError("Invalid queue")


def write_and_submit(output, filename, system, submit=True):
    subfile = filename + '.sub'

    write_file(output, subfile)
    if submit:
        submit_file(subfile, system)
    

def file_submissions(system, *args, **kwargs):
    for infile in os.listdir():
        if not infile.endswith('.in'):
            continue

        filename = infile.split('.')[0]

        if os.path.isfile(filename + ".out"):
            continue

        output = generate_file_output(filename, system, *args)

        write_and_submit(output, filename, system, **kwargs)


def run_directory():
    for infile in os.listdir():
        if not infile.endswith('.in'):
            continue

        filename = infile.split('.')[0]

        if not os.path.isfile(filename + ".out"):
            return True

    return False


def generate_dir_output(filename, system, queue, workdir, path, prog, *args):
    output = get_header(system, queue, filename, *args, path)
    
    if not workdir:
        output += """

tmp=${{TMPDIR}}

cp * $tmp

cd $tmp
"""
    if prog == "psi4":
        output += "\n\nexport MKL_THREADING_LAYER=\"\"\n\n"

    output += """
for file in *.in; do
  if [ ! -f ${file%.in}.out ]]; then"""
    for arg in args:
        print(arg)

    print(prog)
    output += generate_program_input(prog, "${file%.in}", *args)

    if not workdir:
        output += "cp ${{file%.in}}.* {}\ncd {}\n".format(path)

    output += """
  fi
done
"""

    return output  


def directory_submission(system, path, *args, **kwargs):
    if not run_directory():
        return

    filename = os.path.split(path)[-1]

    output = generate_dir_output(filename, system, path, *args)

    write_and_submit(output, filename, system, **kwargs)


def main(*args):
    if len(args) != 8:
        raise ValueError("Invalid input arguments, length = {}".format(len(args)))
    nnodes = int(args[0])
    ncpu = int(args[1])
    time = args[2]
    wd = args[3]
    files = args[4]
    prog = args[5]
    queue = args[6]
    print_level = int(args[7]) 
 
    path = os.path.abspath(wd)

    hostname = os.uname().nodename
    system, mem, workdir = get_host_specs(hostname, queue, ncpu)
    
    kwargs = {"submit": False}
    
    if print_level > 0:
        print("Hostname: {}".format(hostname))
        print("Queueing system: {}".format(queue))
        print("Program: {}".format(prog))
        print("Filepath: {}".format(path))
        if workdir:
            print(" -- Using current dir as working dir")
        else:
            print(" -- Using tmp dir as working dir")
        print()
        print("Number of nodes: {}".format(nnodes))
        print("Number of CPUs per node: {}".format(ncpu))
        print("Time: {}".format(time))

    if files == "files":
        if nnodes > 1:
            raise ValueError("No MPI for file submission")
        if print_level > 0:
            print(" -- Submitting files individually")
        file_submissions(system, queue, workdir, prog, time, nnodes, ncpu, mem, path, **kwargs)
    elif files == "all":
        if print_level > 0:
            print(" -- Submitting all files using single submission")
        directory_submission(system, path, queue, workdir, prog, time, nnodes, ncpu, mem, **kwargs)
    else:
        raise ValueError("Invalid file submmission method: {}".format(files))
 

if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    main(*args)

  
