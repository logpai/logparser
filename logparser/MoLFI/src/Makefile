

# Install the MoLFI tool

REQ_FILE = requirements.txt
PYTHONPATH := $(PWD)

targets:
	@ make init

init:
	@ pip install -r $(REQ_FILE)
	@ python3.6 setup.py install
	@ export PYTHONPATH=$PWD
