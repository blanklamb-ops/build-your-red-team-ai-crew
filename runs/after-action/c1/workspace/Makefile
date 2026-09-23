.PHONY: test clean help

help:
	@echo "after-action — Post-Engagement Report Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  make test        Run acceptance tests on fixture data"
	@echo "  make clean       Remove generated reports and caches"
	@echo "  make help        Show this help message"

test:
	@echo "Running after-action acceptance tests..."
	@echo ""
	@echo "==> Generating reports from fixture engagement..."
	./after_action.py testdata/fixture_engagement/ -o output/
	@echo ""
	@echo "==> Verifying output files exist..."
	@test -f output/client_report.md && echo "✓ Client report generated" || (echo "✗ Client report missing" && exit 1)
	@test -f output/internal_report.md && echo "✓ Internal report generated" || (echo "✗ Internal report missing" && exit 1)
	@test -f output/metadata.json && echo "✓ Metadata generated" || (echo "✗ Metadata missing" && exit 1)
	@echo ""
	@echo "==> Verifying redaction..."
	@! grep -q "sk-proj-ABCdef123456789" output/client_report.md && echo "✓ Secret key redacted in client report" || (echo "✗ Secret key leaked in client report" && exit 1)
	@! grep -q "admin@target.local" output/client_report.md && echo "✓ Email address redacted in client report" || (echo "✗ Email leaked in client report" && exit 1)
	@grep -q "REDACTED" output/client_report.md && echo "✓ Redaction markers present" || (echo "✗ No redaction markers found" && exit 1)
	@echo ""
	@echo "==> Verifying report content..."
	@grep -q "Executive Summary" output/client_report.md && echo "✓ Client report has executive summary" || (echo "✗ Missing executive summary" && exit 1)
	@grep -q "Assessment Timeline" output/client_report.md && echo "✓ Client report has timeline" || (echo "✗ Missing timeline" && exit 1)
	@grep -q "Detection Recommendations" output/client_report.md && echo "✓ Client report has detection recommendations" || (echo "✗ Missing detection recommendations" && exit 1)
	@grep -q "Successes" output/internal_report.md && echo "✓ Internal report has successes section" || (echo "✗ Missing successes" && exit 1)
	@grep -q "Failures" output/internal_report.md && echo "✓ Internal report has failures section" || (echo "✗ Missing failures" && exit 1)
	@echo ""
	@echo "==> Checking correlation..."
	@grep -q "Correlation" output/internal_report.md && echo "✓ Correlation analysis present" || (echo "✗ Missing correlation" && exit 1)
	@echo ""
	@echo "==> Counting correlated items..."
	@python3 -c "import json; data = json.load(open('output/metadata.json')); print(f\"  Events: {data['total_events']}, Decisions: {data['total_decisions']}\")"
	@echo ""
	@echo "✓ All acceptance tests passed!"

clean:
	@echo "Cleaning up generated files..."
	rm -rf output/
	rm -rf __pycache__/
	rm -rf adapters/__pycache__/
	rm -rf renderers/__pycache__/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✓ Clean complete"
