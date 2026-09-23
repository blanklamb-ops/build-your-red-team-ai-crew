package telemetry

import (
	"database/sql"
	"fmt"
	"os"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// RSVPStore manages RSVP event storage and retrieval
type RSVPStore interface {
	RecordResponse(event RSVPEvent) error
	GetResponses(campaignID string) ([]RSVPEvent, error)
	Close() error
}

// SQLiteStore implements RSVPStore using SQLite
type SQLiteStore struct {
	db *sql.DB
}

// NewSQLiteStore creates a new SQLite-backed RSVP store
func NewSQLiteStore(dbPath string) (*SQLiteStore, error) {
	// Check if database exists
	newDB := false
	if _, err := os.Stat(dbPath); os.IsNotExist(err) {
		newDB = true
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	store := &SQLiteStore{db: db}

	// Create schema if new database
	if newDB {
		if err := store.initSchema(); err != nil {
			db.Close()
			return nil, fmt.Errorf("failed to initialize schema: %w", err)
		}

		// Set restrictive permissions (owner read/write only)
		if err := os.Chmod(dbPath, 0600); err != nil {
			db.Close()
			return nil, fmt.Errorf("failed to set database permissions: %w", err)
		}
	}

	return store, nil
}

func (s *SQLiteStore) initSchema() error {
	schema := `
	CREATE TABLE IF NOT EXISTS rsvp_events (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		recipient_id TEXT NOT NULL,
		campaign_id TEXT NOT NULL,
		status INTEGER NOT NULL,
		timestamp DATETIME NOT NULL,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);
	CREATE INDEX IF NOT EXISTS idx_campaign_id ON rsvp_events(campaign_id);
	CREATE INDEX IF NOT EXISTS idx_recipient_id ON rsvp_events(recipient_id);
	`

	_, err := s.db.Exec(schema)
	return err
}

// RecordResponse stores an RSVP event
func (s *SQLiteStore) RecordResponse(event RSVPEvent) error {
	if event.Timestamp.IsZero() {
		event.Timestamp = time.Now()
	}

	query := `
		INSERT INTO rsvp_events (recipient_id, campaign_id, status, timestamp)
		VALUES (?, ?, ?, ?)
	`

	_, err := s.db.Exec(query, event.RecipientID, event.CampaignID, event.Status, event.Timestamp)
	if err != nil {
		return fmt.Errorf("failed to record RSVP: %w", err)
	}

	return nil
}

// GetResponses retrieves all RSVP events for a campaign
func (s *SQLiteStore) GetResponses(campaignID string) ([]RSVPEvent, error) {
	query := `
		SELECT id, recipient_id, campaign_id, status, timestamp
		FROM rsvp_events
		WHERE campaign_id = ?
		ORDER BY timestamp ASC
	`

	rows, err := s.db.Query(query, campaignID)
	if err != nil {
		return nil, fmt.Errorf("failed to query RSVP events: %w", err)
	}
	defer rows.Close()

	var events []RSVPEvent
	for rows.Next() {
		var event RSVPEvent
		var statusInt int
		if err := rows.Scan(&event.ID, &event.RecipientID, &event.CampaignID, &statusInt, &event.Timestamp); err != nil {
			return nil, fmt.Errorf("failed to scan RSVP event: %w", err)
		}
		event.Status = ResponseStatus(statusInt)
		events = append(events, event)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating RSVP events: %w", err)
	}

	return events, nil
}

// Close closes the database connection
func (s *SQLiteStore) Close() error {
	return s.db.Close()
}
