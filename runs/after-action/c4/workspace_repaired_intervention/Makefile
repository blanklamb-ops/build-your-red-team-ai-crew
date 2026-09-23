.PHONY: build test

build:
	PYTHONPATH=. python3 -m src.cli build --engagement testdata/fixture_engagement --out out

test:
	PYTHONPATH=. python3 -m unittest discover -s tests -v
