Demo
====

The logparser toolkit is implemented with Python and requires a number of `dependency requirements <./installation/dependency.html>`_ installed. Users are encouraged to set up the local environment for logparser with Anaconda. However, for ease of reproducing our benchmark results, we have built `docker images <https://hub.docker.com/u/logpai/>`_ for the running evironments. Docker is a popular container technology used in production. If you have `docker installed <./installation/install_docker.html>`_, you can easily pull and run docker containers as follows::

    $ mkdir logparser 
    $ docker run --name logparser_py2 -it -v logparser:/logparser logpai/logparser:py2 bash

Note that if you are going to try MoLFI, which requires Python 3, please run the following container::

    $ mkdir logparser
    $ docker run --name logparser_py3 -it -v logparser:/logparser logpai/logparser:py3 bash


After starting the docker containers, you can run the demos of logparser on the `HDFS sample log <https://github.com/logpai/loghub/tree/master/HDFS>`_::

    $ git clone https://github.com/logpai/logparser.git /logparser/
    $ cd /logparser/demo/
    $ python Drain_demo.py

The logparser demo/benchmark scripts will produce both event templates and structured logs in the result directory:

- HDFS_2k.log_templates.csv
- HDFS_2k.log_structured.csv 




