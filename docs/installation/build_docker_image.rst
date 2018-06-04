Build docker image
==================

Build logpai/logparser:py2
::

    $ sudo docker run --name logparser_py2 -it ubuntu:16.04 bash

    $ apt-get update
    $ apt-get install -y wget bzip2
    $ apt-get install -y gcc perl git
    $ rm -rf /var/lib/apt/lists/*

    $ cd /
    $ mkdir anaconda
    $ cd anaconda
    $ wget https://repo.anaconda.com/archive/Anaconda2-5.2.0-Linux-x86_64.sh
    $ bash Anaconda2-5.2.0-Linux-x86_64.sh 
    $ source ~/.bashrc
    $ cd ..
    $ rm -r anaconda
    $ exit

    $ docker commit logparser_py2 logpai/logparser:py2
    $ docker login
    $ docker push logpai/logparser:py2

    
Build logpai/logparser:py3
::

    $ sudo docker run --name logparser_py3 -it ubuntu:16.04 bash

    $ apt-get update
    $ apt-get install -y wget bzip2 git
    $ rm -rf /var/lib/apt/lists/*

    $ cd /
    $ mkdir anaconda
    $ cd anaconda
    $ wget https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh
    $ bash Anaconda3-5.1.0-Linux-x86_64.sh 
    $ source ~/.bashrc
    $ cd ..
    $ rm -r anaconda

    $ pip install deap
    $ exit

    $ docker commit logparser_py3 logpai/logparser:py3
    $ docker login
    $ docker push logpai/logparser:py3