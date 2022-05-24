FROM continuumio/miniconda3
#  FROM python:3.9-slim

WORKDIR /home

COPY env.yml .
RUN conda env create -f env.yml
SHELL ["conda", "run", "-n", "vivarium-models", "/bin/bash", "-c"]
# RUN ["/bin/bash", "-c", "conda", "activate", "vivarium-models"]
# RUN ["conda", "env", "list"]

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "vivarium-models", "python", "-m", "vivarium_models.composites.actin_fiber"]

# RUN conda activate vivarium-models
# RUN conda init bash
# RUN ["conda", "init", "bash"]
#  RUN conda activate vivarium-models


