init:
	pip install -r requirements.txt

test:
	py.test tests/test_flacthis.py

test3:
	python3 -m pytest tests/test_flacthis.py

.PHONY: init test test3
