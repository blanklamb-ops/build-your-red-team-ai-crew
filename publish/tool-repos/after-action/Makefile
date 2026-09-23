.PHONY: fixture test scanners acceptance clean

fixture:
	python3 -m after_action.cli testdata/fixture_engagement --output reports/fixture

test:
	python3 -m unittest discover -s tests -v

scanners:
	./scripts/archive_scanners.sh

acceptance: test fixture
	python3 scripts/acceptance.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -r {} +
	rm -r reports/fixture 2>/dev/null || true
