.PHONY: help test-run verify-redaction test clean

help:
	@echo "After-Action Report Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  make test-run         - Generate reports from fixture engagement data"
	@echo "  make verify-redaction - Verify planted secret is redacted"
	@echo "  make test            - Run integration tests"
	@echo "  make clean           - Remove generated reports"

test-run:
	@echo "Generating reports from fixture engagement..."
	python -m after_action.cli \
		--logs testdata/fixture_engagement/logs/ \
		--decisions testdata/fixture_engagement/decisions.jsonl \
		--output reports/fixture \
		--engagement-name "Fixture Security Assessment" \
		--verbose
	@echo ""
	@echo "Reports generated in reports/fixture/"
	@echo "  - client_report.md"
	@echo "  - internal_learning.md"

verify-redaction:
	@echo "Verifying redaction of planted secret..."
	@python -m after_action.cli \
		--logs testdata/fixture_engagement/logs/ \
		--decisions testdata/fixture_engagement/decisions.jsonl \
		--output reports/redaction-test \
		--engagement-name "Redaction Test" \
		--verbose > /dev/null 2>&1
	@if grep -q "sk-1234567890abcdef1234567890abcdef" reports/redaction-test/client_report.md; then \
		echo "❌ FAIL: Planted secret found in client report (not redacted)"; \
		exit 1; \
	else \
		echo "✓ PASS: Planted secret successfully redacted from client report"; \
	fi
	@if grep -q "\[REDACTED" reports/redaction-test/client_report.md; then \
		echo "✓ PASS: Redaction markers present in client report"; \
	else \
		echo "⚠ WARNING: No redaction markers found (may be OK if no secrets detected)"; \
	fi

test:
	@echo "Running integration tests..."
	python -m pytest tests/test_integration.py -v

clean:
	@echo "Cleaning generated reports..."
	rm -rf reports/
	rm -rf __pycache__
	rm -rf after_action/__pycache__
	rm -rf tests/__pycache__
	@echo "Clean complete"
