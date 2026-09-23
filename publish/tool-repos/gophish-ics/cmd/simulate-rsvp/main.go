package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/research/gophish-ics/pkg/telemetry"
)

func main() {
	dbPath := flag.String("db-path", "./telemetry.db", "Path to telemetry database")
	fixturePath := flag.String("fixture", "", "Path to RSVP fixture JSON file (required)")

	flag.Parse()

	if *fixturePath == "" {
		fmt.Fprintln(os.Stderr, "Error: --fixture is required")
		flag.Usage()
		os.Exit(1)
	}

	// Load fixture data
	fixtureData, err := os.ReadFile(*fixturePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read fixture file: %v\n", err)
		os.Exit(1)
	}

	var events []struct {
		RecipientID string `json:"recipient_id"`
		CampaignID  string `json:"campaign_id"`
		Status      string `json:"status"`
	}

	if err := json.Unmarshal(fixtureData, &events); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to parse fixture JSON: %v\n", err)
		os.Exit(1)
	}

	// Open telemetry store
	store, err := telemetry.NewSQLiteStore(*dbPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open telemetry database: %v\n", err)
		os.Exit(1)
	}
	defer store.Close()

	// Record events
	for _, event := range events {
		rsvpEvent := telemetry.RSVPEvent{
			RecipientID: event.RecipientID,
			CampaignID:  event.CampaignID,
			Status:      telemetry.ParseResponseStatus(event.Status),
		}

		if err := store.RecordResponse(rsvpEvent); err != nil {
			fmt.Fprintf(os.Stderr, "Failed to record RSVP event: %v\n", err)
			os.Exit(1)
		}
	}

	fmt.Fprintf(os.Stderr, "Loaded %d RSVP events from fixture\n", len(events))
}
