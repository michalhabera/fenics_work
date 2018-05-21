# SIMD FEniCS project

Working repository for the FEniCS Google Summer of Code SIMD project.

## Docker image

This repository provides a Dockerfile with all required components. In the root folder of the repository run
```
docker build -t simd-work .
```
then start container with
```
docker run -v ~/fenics_work/main:/local/fenics -it simd-work /bin/bash
```

## Installing FEniCS locally
### Required packages
The [dolfinx Dockerfile](https://github.com/FEniCS/dolfinx/blob/master/Dockerfile) shows which packages are required.
As a single command:
```
sudo apt-get -y install \
    cmake \
    doxygen \
    g++ \
    gfortran \
    git \
    gmsh \
    graphviz \
    libboost-dev \
    libboost-filesystem-dev \
    libboost-iostreams-dev \
    libboost-math-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-thread-dev \
    libboost-timer-dev \
    libeigen3-dev \
    libhdf5-openmpi-dev \
    liblapack-dev \
    libopenmpi-dev \
    libopenblas-dev \
    openmpi-bin \
    pkg-config \
    python3-dev \
    valgrind \
    wget \
    bash-completion
```

### Install script
The `install_fenics.py` script downloads all major FEniCS components (fiat, ufl, dijisto, ffcx, dolfinx and Firedrake's tsfc, coffee, finat) from their repositories (master branch) and installs them in a python virtual environment.

#### Options
Currently, the script has the following options:
```
usage: install_fenics.py [-h] [-r REPO_DIR] [-y] [-l | -co] [-j JOBS]
                         [install_prefix]

install and set up an environment for FEniCS from git

positional arguments:
  install_prefix        FEniCS will be installed into this folder. If not
                        specified, the current folder will be used.

optional arguments:
  -h, --help            show this help message and exit
  -r REPO_DIR, --repo-dir REPO_DIR
                        Directory where source directories (repositories) will
                        be stored/are already located.
  -y, --yes             Respond with 'yes' to all confirmation messages.
  -l, --local           Don't clone any repositories, use local files.
  -co, --clone-only     Only clone the required repositories, no
                        install/build.
  -j JOBS, --jobs JOBS  Number of make jobs to issue for building DOLFIN ('-j'
                        parameter for make). Default is to use
                        'os.cpu_count()'.
```
The `install_prefix` will contain the `fenics_env` virtual environment, the `dolfin` install directory, etc.

#### Virtual environment
In order to run the script, the `virtualenv` and `click` python packages are required. Install it using:
```
pip3 install virtualenv click
```
Optionally, add the user python bin directory to your path in `~/.profile`:
```
export PATH=$PATH:~/.local/bin
```

## Activating the environment
If the installtion folder was specified as `~/fenics`, the proper environment can be activated by
```
source ~/fenics/fenics_env/bin/activate
source ~/fenics/dolfinx/share/dolfin/dolfin.conf
export PETSC_DIR=~/fenics/petsc
export SLEPC_DIR=~/fenics/slepc
```

## Debugging

On Ubuntu the default core file size limit is 0. Use
```
ulimit -c unlimited
```
to remove this restrictions. However this has to be rerun in every shell session.
The core dumps will be located in the working directory. They can be inspected by launching
```
gdb <executable path> <core dump path>
```
followed by the `bt` (backtrace) command inside `gdb`. The command `quit` can be used to exit `gdb`.
