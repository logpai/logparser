Install docker
==============

This is a note showing the steps of installing docker on Ubuntu platforms. If you need more detailed information, please check docker documentaion at: https://docs.docker.com/install/linux/docker-ce/ubuntu


.. note::
    Uninstall old docker versions if any::

        $ sudo apt-get remove docker docker-engine docker.io

- **Ubuntu 14.04**

    Install `linux-image-extra-*` to allow Docker to use the aufs storage drivers.
    ::

        $ sudo apt-get update

        $ sudo apt-get install \
            linux-image-extra-$(uname -r) \
            linux-image-extra-virtual

    Download docker package file `docker-ce_17.03.2~ce-0~ubuntu-trusty_amd64.deb <https://download.docker.com/linux/ubuntu/dists/trusty/pool/stable/amd64/docker-ce_17.03.2~ce-0~ubuntu-trusty_amd64.deb>`_.
    ::

        $ sudo dpkg -i ~/docker/docker-ce_17.03.2~ce-0~ubuntu-trusty_amd64.deb


- **Ubuntu 16.04**

    Download docker package file `docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb <https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb>`_.
    ::

        $ sudo dpkg -i ~/docker/docker-ce_17.03.2~ce-0~ubuntu-xenial_amd64.deb

Verify that Docker CE is installed correctly by running the hello-world image::

    $ sudo docker run hello-world

Add user to the docker group to run docker commands without sudo::

    $ sudo groupadd docker
    $ sudo usermod -aG docker $USER