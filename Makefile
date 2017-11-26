init:
	pip install -r requirements.txt

test:
	py.test tests/test_flacthis.py

.PHONY: init test
