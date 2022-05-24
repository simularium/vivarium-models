# vivarium-models

Connecting Simularium prototypes together using Vivarium

---

# Installation

First, we recommend you create an environment (with pyenv, conda, or similar).

Then, to install:
**Stable Release:** `pip install vivarium_medyan` (coming soon)<br>
**Development Head:** `pip install git+https://github.com/vivarium-collective/vivarium-MEDYAN.git`<br>

## Local editable installation with pyenv + conda

To see all pyenv versions:

```
pyenv install list
```

To install a particular version of python (or conda):

```
pyenv install anaconda3-5.3.1
```

Install dependencies using pyenv + conda:

```
pyenv local anaconda3-5.3.1 # or whatever version you have installed
pyenv virtualenv vivarium-models
pyenv local vivarium-models
conda env update -f env.yml
```

## Local editable installation with conda alone

Install conda: https://docs.conda.io/en/latest/miniconda.html

Using conda, you can run

```
conda env create -f env.yml
conda activate vivarium-models
```

which will create and then activate a conda environment called `vivarium-models` with all the required dependencies (including ReaDDy) installed.

To update:

```
conda env update -f env.yml
```

### MEDYAN Installation

Download the MEDYAN source here: http://medyan.org/download.html

Unzip and cd into that dir, then at the command line:

```
./conf.sh
cd build
make
```

### Cytosim Installation

First, clone the repo:

    git clone https://gitlab.com/f-nedelec/cytosim.git

Change the header to allow for 3d (in file src/math/dim.h)

    #define DIM 3 # instead of 2

Then, make the executable (avoid the GLEW functionality):

    make sim
    make report

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

## Commands You Need To Know

1. `black vivarium_models`

    This will fix lint issues.

2. `make build`

    This will run `tox` which will run all your tests as well as lint your code.

3. `make clean`

    This will clean up various Python and build generated files so that you can ensure that you are working in a clean environment.
    
4. `make docs`

    This will generate and launch a web browser to view the most up-to-date
    documentation for your Python package.
