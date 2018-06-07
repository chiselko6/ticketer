all: install

install:
	python setup.py install --record "${SETUP_RECORD}"
