PYTHON3 = python3

#part makefile that are not dep on specific file
.PHONY: all

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make build"
	@echo "To test the project type make tests"
	@echo "To extensively test the project type make ext_tests"
	@echo "To check syntax type make lint"
	@echo "To clean outputs of the project type make clean"
	@echo "------------------------------------"



all: build

build:
	$(PYTHON3) setup.py build_ext  --inplace
	
clean:
	@/usr/bin/find . -name '*.pyc' -delete
	# delete output dir in ext_tests

lint:
	$(PYTHON3) setup.py flake8

tests:
	@echo -e "\n*** Running unit tests smartstopos"
	$(PYTHON3) setup.py test

ext_tests: 
	@echo -e "\n*** Running extended tests smartstopos"
	cd ext_tests/single/src/  && bash run_local.sh || exit 
	@echo "****Test single run completed"
	cd ext_tests/opt/src/  && bash run_local.sh || exit 
	@echo "****Test opt run completed"
	cd ext_tests/file/src/  && bash run_local.sh || exit  
	@echo "****Test single run completed from file"

verify: clean python-deps lint tests ext_tests

.PHONY: clean lint python-deps tests verify ext_tests 
