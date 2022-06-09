# vivarium-models

[![Build Status](https://github.com/simularium/vivarium_models/workflows/Build%20Main/badge.svg)](https://github.com/simularium/vivarium_models/actions)
[![Documentation](https://github.com/simularium/vivarium_models/workflows/Documentation/badge.svg)](https://simularium.github.io/vivarium_models/)
[![Code Coverage](https://codecov.io/gh/simularium/vivarium_models/branch/main/graph/badge.svg)](https://codecov.io/gh/simularium/vivarium_models)

Connecting Simularium prototypes together using Vivarium

---

# Installation

## Docker

First, install Docker (https://docs.docker.com/engine/install/). Using Docker, you can avoid building and installing the simulation engine dependencies.

If using a package manager, like homebrew for mac, use `brew install --cask docker`
then open the Docker app in Applications/ and give it permissions.

## Installation with pyenv + conda

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

## Installation with conda alone

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

## Alternatively:

**Stable Release:** `pip install vivarium_models` (coming soon)<br>
**Development Head:** `pip install git+https://github.com/simularium/vivarium-models.git`

ReaDDy models depend on ReaDDy, which requires conda. Install ReaDDy with `conda install -c readdy/label/dev readdy` after adding the conda-forge channel `conda config --add channels conda-forge`

## Documentation

For full package documentation please visit [simularium.github.io/vivarium_models](https://simularium.github.io/vivarium_models).

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
