init:
	pip install -r requirements.txt

dev:
	pip install -r dev_requirements.txt

dev3:
	pip3 install -r dev_requirements.txt

test:
	py.test tests/test_flacthis.py

test3:
	python3 -m pytest tests/test_flacthis.py

.PHONY: init test test3 dev dev3
