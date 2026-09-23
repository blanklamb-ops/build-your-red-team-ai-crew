package telemetry

import (
	"path/filepath"
	"testing"
	"time"
)

func TestReporter_AggregatesCounts(t *testing.T) {
	tmpDir := t.TempDir()
	dbPath := filepath.Join(tmpDir, "test-reporter.db")

	store, err := NewSQLiteStore(dbPath)
	if err != nil {
		t.Fatalf("Failed to create store: %v", err)
	}
	defer store.Close()

	campaignID := "report-test-001"

	// Load fixture events
	fixtureEvents := []RSVPEvent{
		{RecipientID: "r1", CampaignID: campaignID, Status: StatusAccept, Timestamp: time.Now()},
		{RecipientID: "r2", CampaignID: campaignID, Status: StatusAccept, Timestamp: time.Now()},
		{RecipientID: "r3", CampaignID: campaignID, Status: StatusDecline, Timestamp: time.Now()},
		{RecipientID: "r4", CampaignID: campaignID, Status: StatusTentative, Timestamp: time.Now()},
		// r5 and r6 did not respond
	}

	for _, event := range fixtureEvents {
		if err := store.RecordResponse(event); err != nil {
			t.Fatalf("Failed to record event: %v", err)
		}
	}

	// Generate report
	totalSent := 6
	report, err := GenerateCampaignReport(campaignID, totalSent, store)
	if err != nil {
		t.Fatalf("Failed to generate report: %v", err)
	}

	// Validate counts
	if report.TotalSent != 6 {
		t.Errorf("TotalSent = %d, want 6", report.TotalSent)
	}
	if report.AcceptCount != 2 {
		t.Errorf("AcceptCount = %d, want 2", report.AcceptCount)
	}
	if report.DeclineCount != 1 {
		t.Errorf("DeclineCount = %d, want 1", report.DeclineCount)
	}
	if report.TentativeCount != 1 {
		t.Errorf("TentativeCount = %d, want 1", report.TentativeCount)
	}
	if report.NoResponseCount != 2 {
		t.Errorf("NoResponseCount = %d, want 2", report.NoResponseCount)
	}
}
