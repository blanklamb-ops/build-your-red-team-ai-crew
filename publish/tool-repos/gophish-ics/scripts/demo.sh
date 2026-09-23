#!/bin/bash
# Demo script for gophish-ics
# Runs end-to-end workflow with synthetic test data

set -e

echo "========================================="
echo "gophish-ics Lab Demo"
echo "========================================="
echo ""

# Safety check: verify default config is still disabled
echo "[1/5] Safety check: verifying config/config.yaml has ics_enabled: false"
if grep -q "ics_enabled: true" config/config.yaml; then
    echo "ERROR: Default config has ics_enabled: true. This violates lab safety."
    echo "Please reset config/config.yaml to ics_enabled: false before running demo."
    exit 1
fi
echo "✓ Config safety verified"
echo ""

# Build CLI tools
echo "[2/5] Building CLI tools..."
go build -o bin/generate ./cmd/generate
go build -o bin/simulate-rsvp ./cmd/simulate-rsvp
go build -o bin/report ./cmd/report
echo "✓ Build complete"
echo ""

# Generate ICS from fixture (using --enable-ics override for demo)
echo "[3/5] Generating ICS file from campaign fixture..."
./bin/generate \
    --config config/config.yaml \
    --input testdata/campaign_fixture.json \
    --output output/demo-meeting.ics \
    --enable-ics \
    --demo

echo "✓ ICS file created: output/demo-meeting.ics"
echo ""
echo "Sample ICS content:"
head -n 20 output/demo-meeting.ics
echo "..."
echo ""

# Load RSVP fixture data
echo "[4/5] Loading RSVP fixture data..."
./bin/simulate-rsvp \
    --db-path ./telemetry.db \
    --fixture testdata/rsvp_fixture.json
echo "✓ RSVP data loaded"
echo ""

# Generate and display report
echo "[5/5] Generating RSVP report..."
./bin/report \
    --db-path ./telemetry.db \
    --campaign-id fixture-campaign-001 \
    --total-sent 8
echo ""

echo "========================================="
echo "Demo complete!"
echo "========================================="
echo ""
echo "To clean up demo artifacts:"
echo "  rm -f telemetry.db output/demo-meeting.ics"
echo ""
echo "IMPORTANT: This demo used --enable-ics flag override."
echo "The checked-in config still has ics_enabled: false for safety."
