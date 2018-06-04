
```Bash
sudo docker run -i -t ubuntu:16.04 bash 

cd home
mkdir anaconda
cd anaconda

apt-get update
apt-get install -y wget nano bzip2
apt-get install -y gcc perl git
rm -rf /var/lib/apt/lists/*

wget https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh
bash Anaconda3-5.1.0-Linux-x86_64.sh 
source ~/.bashrc

cd ~
rm -r anaconda
pip install deap

conda create --name pyenv2 anaconda python=2.7

git clone https://github.com/logpai/logparser

sudo docker commit df888c72ed5a logparser
docker login
docker tag logparser logpai/logparser
docker push logpai/logparser
```

sudo docker run -it logpai/logparser bash

cd ~/logparser/demo
source activate pyenv2
python drain_demo.py
source deactivate

python MoLFI_demo.py

Multiple files contained by the folder src can be copied into the target folder using:

docker cp src/. mycontainer:/target
docker cp mycontainer:/src/. target