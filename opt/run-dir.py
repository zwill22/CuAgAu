import os
import subprocess


def get_header(filename, **kwargs):
    system = kwargs["system"]
    queue = kwargs["queue"]

    args = [kwargs[k] for k in ("time", "nodes", "ncpu", "mem", "path")]

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
#SBATCH --tasks-per-node={3}
#SBATCH --time={1}
#SBATCH --job-name="{0}"
#SBATCH --error="{0}.e%j"
#SBATCH --output="{0}.o%j"
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

    return output.format(filename, *args)


def get_host_specs(**data):
    ncpu = data.get("ncpu")
    hostname = data.get("hostname")
    queue = data.get("queue")

    if ncpu < 0:
        raise ValueError("Number of cpus cannot be negative")

    if "newblue" in hostname:
        system = 'pbs'
        if ncpu > 16:
            raise ValueError("Too many cpus ({} > 16) for BC3".format(ncpu))
        if queue == "himem":
            mem = 15
        else:
            mem = 4
        workdir = True
    elif 'bc4' in hostname:
        system = 'slurm'
        if ncpu > 28:
            raise ValueError("Too many cpus ({} > 28) for BC4".format(ncpu))
        if queue == "himem":
            mem = 18
        else:
            mem = 5
        workdir = True
    elif 'bp1' in hostname:
        system = 'slurm'
        if queue == "amd":
            mem = 7
            if ncpu > 120:
                raise ValueError("Too many cpus BP1 (amd): {}".format(ncpu))
        elif queue == "highmem":
            mem = 90
            if ncpu > 8:
                raise ValueError("Too many cpus BP1 (highmem): {}".format(ncpu))
        elif queue == "plong":
            mem = 10
            if ncpu > 32:
                raise ValueError("Too many cpus BP1 (plong): {}".format(ncpu))
        else:
            mem = 5
            if ncpu > 32:
                raise ValueError("Too many cpus BP1: {} > 32".format(ncpu))
        workdir = False
    else:
        raise ValueError("Unable to determine identity of host computer")

    return system, mem * ncpu, workdir
 

def generate_program_input(filename, single=True, **kwargs):
    prog = kwargs["prog"]
    ncpu = kwargs["ncpu"]

    if single:
        output = "\n\n"
    else:
        output = "\n\t"
    if prog == "qcore":
        output += "qcore -n {1} \"{0}.in\" &> \"{0}.out\""
    elif prog == "orca":
        output += "$((which orca)) \"{0}.in\" &> \"{0}.out\""
    elif prog == "psi4":
        if single:
            output += "export MKL_THREADING_LAYER=\"\"\n\n"
        output += "psi4 -n {1} -i \"{0}.in\" -o \"{0}.out\""
    else:
        raise ValueError("Unrecognised program: {}".format(prog)) 
    if single:
        output += "\n"

    return output.format(filename, ncpu)


def generate_file_output(filename, **kwargs):
    output = get_header(filename, **kwargs)

    workdir = kwargs["workdir"]
    if not workdir:
        output += """

tmp=${{TMPDIR}}

cp "{0}.in" $tmp
cp "{0}.xyz" $tmp

cd $tmp
""".format(filename)
    
    output += generate_program_input(filename, **kwargs)

    path = kwargs["path"]
    if not workdir:
        output += "\ncp {0}* {1}\ncd {1}\n".format(filename, path)

    return output


def write_file(output, subfile):
    with open(subfile, 'w') as f:
        f.write(output) 
    

def submit_file(subfile, **kwargs):
    system = kwargs["system"]

    if system == 'pbs':
        subprocess.run(["qsub", subfile])
    elif system == 'slurm':
        subprocess.run(["sbatch", subfile])
    else:
        raise ValueError("Invalid queue")


def write_and_submit(output, filename, submit=True, **kwargs):
    path = kwargs["path"]
    subfilepath = os.path.join(path, filename + '.sub')

    write_file(output, subfilepath)
    if submit:
        submit_file(subfilepath, **kwargs)
    

def file_submissions(write=True, **kwargs):
    path = kwargs["path"]
    for infile in os.listdir(path):
        if not infile.endswith('.in'):
            continue

        filename = infile.split('.')[0]

        outfile_path = os.path.join(path, filename + ".out")

        if os.path.isfile(outfile_path):
            continue

        output = generate_file_output(filename, **kwargs)

        if write:
            write_and_submit(output, filename, **kwargs)
        else:
            print(output)


def run_directory():
    for infile in os.listdir():
        if not infile.endswith('.in'):
            continue

        filename = infile.split('.')[0]

        if not os.path.isfile(filename + ".out"):
            return True

    return False


def generate_dir_output(filename, **kwargs):
    output = get_header(filename, **kwargs)

    workdir = kwargs["workdir"]
    prog = kwargs["prog"]
    path = kwargs["path"]

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

    output += generate_program_input("${file%.in}", **kwargs, single=False)

    if not workdir:
        output += "cp ${{file%.in}}.* {0}\ncd {0}\n".format(path)

    output += """
  fi
done
"""

    return output  


def directory_submission(write=True, **kwargs):
    path = kwargs["path"]

    if not run_directory():
        return

    filename = os.path.split(path)[-1]

    output = generate_dir_output(filename, **kwargs)

    if write:
        write_and_submit(output, filename, **kwargs)
    else:
        print()
        print(output)


def main(*args):
    narg = len(args)
    if len(args) != 7:
        raise ValueError("Invalid number of input arguments ({})".format(narg))

    names = ["nodes", "ncpu", "time", "wd", "files", "prog", "queue"]

    data = dict(zip(names, args))
    data["ncpu"] = int(data["ncpu"])
    data["nodes"] = int(data["nodes"])

    data["path"] = os.path.abspath(data["wd"])

    hostname = os.uname().nodename
    data["hostname"] = hostname
    data["system"], data["mem"], data["workdir"] = get_host_specs(**data)

    files = data["files"]
    nodes = data["nodes"]

    if files == "files":
        if nodes > 1:
            raise ValueError("No MPI for file submission")
        file_submissions(**data)
    elif files == "all":
        directory_submission(**data)
    else:
        raise ValueError("Invalid file submission method: {}".format(files))
 

if __name__ == "__main__":
    import sys

    argv = sys.argv[1:]

    main(*argv)
