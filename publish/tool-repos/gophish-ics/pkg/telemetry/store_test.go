package telemetry

import (
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestRSVPStore_RecordAndQuery(t *testing.T) {
	// Create temporary database
	tmpDir := t.TempDir()
	dbPath := filepath.Join(tmpDir, "test-telemetry.db")

	store, err := NewSQLiteStore(dbPath)
	if err != nil {
		t.Fatalf("Failed to create store: %v", err)
	}
	defer store.Close()

	campaignID := "test-campaign-001"

	// Record multiple responses
	events := []RSVPEvent{
		{
			RecipientID: "recipient-1",
			CampaignID:  campaignID,
			Status:      StatusAccept,
			Timestamp:   time.Now(),
		},
		{
			RecipientID: "recipient-2",
			CampaignID:  campaignID,
			Status:      StatusDecline,
			Timestamp:   time.Now(),
		},
		{
			RecipientID: "recipient-3",
			CampaignID:  campaignID,
			Status:      StatusTentative,
			Timestamp:   time.Now(),
		},
	}

	for _, event := range events {
		if err := store.RecordResponse(event); err != nil {
			t.Fatalf("Failed to record response: %v", err)
		}
	}

	// Query responses
	retrieved, err := store.GetResponses(campaignID)
	if err != nil {
		t.Fatalf("Failed to get responses: %v", err)
	}

	if len(retrieved) != 3 {
		t.Errorf("Expected 3 events, got %d", len(retrieved))
	}

	// Verify statuses
	statuses := make(map[ResponseStatus]int)
	for _, event := range retrieved {
		statuses[event.Status]++
	}

	if statuses[StatusAccept] != 1 {
		t.Errorf("Expected 1 accept, got %d", statuses[StatusAccept])
	}
	if statuses[StatusDecline] != 1 {
		t.Errorf("Expected 1 decline, got %d", statuses[StatusDecline])
	}
	if statuses[StatusTentative] != 1 {
		t.Errorf("Expected 1 tentative, got %d", statuses[StatusTentative])
	}
}

func TestSQLiteStore_DatabasePermissions(t *testing.T) {
	tmpDir := t.TempDir()
	dbPath := filepath.Join(tmpDir, "test-perms.db")

	store, err := NewSQLiteStore(dbPath)
	if err != nil {
		t.Fatalf("Failed to create store: %v", err)
	}
	defer store.Close()

	// Check file permissions
	info, err := os.Stat(dbPath)
	if err != nil {
		t.Fatalf("Failed to stat database file: %v", err)
	}

	mode := info.Mode()
	if mode.Perm() != 0600 {
		t.Errorf("Database permissions are %o, expected 0600", mode.Perm())
	}
}

func TestRSVPStore_EmptyCampaign(t *testing.T) {
	tmpDir := t.TempDir()
	dbPath := filepath.Join(tmpDir, "test-empty.db")

	store, err := NewSQLiteStore(dbPath)
	if err != nil {
		t.Fatalf("Failed to create store: %v", err)
	}
	defer store.Close()

	// Query non-existent campaign
	events, err := store.GetResponses("nonexistent-campaign")
	if err != nil {
		t.Fatalf("Query should succeed for empty campaign: %v", err)
	}

	if len(events) != 0 {
		t.Errorf("Expected 0 events, got %d", len(events))
	}
}
