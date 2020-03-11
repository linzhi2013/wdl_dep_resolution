FROM ubuntu:16.04

MAINTAINER Guanliang Meng <linzhi2012[AT]gmail[DOT].com>, GrandOmics, Beijing, China

ENV DEBIAN_FRONTEND=noninteractive


# Install required packages
RUN apt-get update && \
    apt-get install -y  --no-install-recommends wget bzip2 unzip ca-certificates less make g++ zip


# install anaconda
RUN mkdir /app

# wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \

RUN if [ ! -d /app/anaconda ]; then \
        wget -c \
        https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh \
        -O /app/anaconda.sh && \
        bash /app/anaconda.sh -b -p /app/anaconda && \
        rm -rf /app/anaconda.sh ; fi

RUN apt-get clean && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# set anaconda path
ENV PATH="/app/anaconda/bin:$PATH"

COPY environment.yml /environment.yml

# install dependency
RUN conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda config --add channels defaults && \
    conda install -y --file /environment.yml && \
    conda clean -y -a


# install the ones can not be found in the bioconda
COPY scripts /app/scripts

ENV LC_ALL=C
ENV PATH=/app/anaconda/bin:/app/scripts:/app/scripts/HicReport:$PATH

VOLUME /project
WORKDIR /project

CMD ["/bin/bash"]
