package ics

import (
	"strings"
	"testing"
	"time"

	ics "github.com/arran4/golang-ical"
	"github.com/research/gophish-ics/pkg/config"
)

func TestGenerateICS_ValidOutput(t *testing.T) {
	cfg := &config.Config{
		ICSEnabled:  true,
		SafeDomains: []string{"example.com"},
	}

	campaign := Campaign{
		ID:          "test-campaign-001",
		Organizer:   "organizer@example.com",
		Summary:     "Team Meeting",
		Description: "Quarterly review meeting",
		StartTime:   time.Date(2025, 6, 15, 14, 0, 0, 0, time.UTC),
		EndTime:     time.Date(2025, 6, 15, 15, 0, 0, 0, time.UTC),
		Attendees:   []string{"victim1@example.com", "victim2@example.com"},
		Location:    "Conference Room A",
	}

	opts := GeneratorOptions{
		EnableICS:   true,
		SafeDomains: cfg.SafeDomains,
	}

	icsData, err := GenerateICS(cfg, campaign, opts)
	if err != nil {
		t.Fatalf("GenerateICS failed: %v", err)
	}

	icsStr := string(icsData)

	// Check required ICS components
	requiredFields := []string{
		"BEGIN:VCALENDAR",
		"METHOD:REQUEST",
		"BEGIN:VEVENT",
		"UID:test-campaign-001",
		"SUMMARY:Team Meeting",
		"ORGANIZER",
		"organizer@example.com",
		"ATTENDEE",
		"victim1@example.com",
		"victim2@example.com",
		"DTSTART",
		"DTEND",
		"END:VEVENT",
		"END:VCALENDAR",
	}

	for _, field := range requiredFields {
		if !strings.Contains(icsStr, field) {
			t.Errorf("Generated ICS missing required field: %s", field)
		}
	}
}

func TestGenerateICS_ParsesCleanly(t *testing.T) {
	cfg := &config.Config{
		ICSEnabled:  true,
		SafeDomains: []string{"example.com"},
	}

	campaign := Campaign{
		ID:          "parse-test-001",
		Organizer:   "sender@example.com",
		Summary:     "Test Event",
		Description: "Validation test",
		StartTime:   time.Date(2025, 1, 1, 12, 0, 0, 0, time.UTC),
		EndTime:     time.Date(2025, 1, 1, 13, 0, 0, 0, time.UTC),
		Attendees:   []string{"test@example.com"},
	}

	opts := GeneratorOptions{
		EnableICS:   true,
		SafeDomains: cfg.SafeDomains,
	}

	icsData, err := GenerateICS(cfg, campaign, opts)
	if err != nil {
		t.Fatalf("GenerateICS failed: %v", err)
	}

	// Parse with golang-ical library to validate RFC 5545 compliance
	cal, err := ics.ParseCalendar(strings.NewReader(string(icsData)))
	if err != nil {
		t.Fatalf("Generated ICS failed to parse: %v", err)
	}

	// Verify parsed calendar has expected properties
	if len(cal.Events()) != 1 {
		t.Errorf("Expected 1 event, got %d", len(cal.Events()))
	}

	event := cal.Events()[0]
	if event.Id() != "parse-test-001" {
		t.Errorf("Event ID mismatch: got %s, want parse-test-001", event.Id())
	}
}

func TestGenerateICS_DisabledByDefault(t *testing.T) {
	cfg := &config.Config{
		ICSEnabled:  false, // Simulates default config
		SafeDomains: []string{"example.com"},
	}

	campaign := Campaign{
		ID:          "disabled-test",
		Organizer:   "sender@example.com",
		Summary:     "Should Fail",
		Description: "Test",
		StartTime:   time.Now(),
		EndTime:     time.Now().Add(time.Hour),
		Attendees:   []string{"test@example.com"},
	}

	opts := GeneratorOptions{
		EnableICS:   false, // No override
		SafeDomains: cfg.SafeDomains,
	}

	_, err := GenerateICS(cfg, campaign, opts)
	if err == nil {
		t.Fatal("Expected error when ICS disabled, got nil")
	}

	if !strings.Contains(err.Error(), "disabled") {
		t.Errorf("Error should mention 'disabled', got: %v", err)
	}
}

func TestGenerateICS_UnsafeDomainBlocked(t *testing.T) {
	cfg := &config.Config{
		ICSEnabled:  true,
		SafeDomains: []string{"example.com"},
	}

	campaign := Campaign{
		ID:          "unsafe-test",
		Organizer:   "sender@example.com",
		Summary:     "Phishing Test",
		Description: "Should be blocked",
		StartTime:   time.Now(),
		EndTime:     time.Now().Add(time.Hour),
		Attendees:   []string{"victim@realdomain.com"}, // Not in safe list
	}

	opts := GeneratorOptions{
		EnableICS:   true,
		ForceUnsafe: false, // Safety check active
		SafeDomains: cfg.SafeDomains,
	}

	_, err := GenerateICS(cfg, campaign, opts)
	if err == nil {
		t.Fatal("Expected error for unsafe domain, got nil")
	}

	if !strings.Contains(err.Error(), "unsafe") {
		t.Errorf("Error should mention 'unsafe', got: %v", err)
	}
}

func TestGenerateICS_ForceBypass(t *testing.T) {
	cfg := &config.Config{
		ICSEnabled:  true,
		SafeDomains: []string{"example.com"},
	}

	campaign := Campaign{
		ID:          "force-test",
		Organizer:   "sender@example.com",
		Summary:     "Authorized Test",
		Description: "Force mode active",
		StartTime:   time.Now(),
		EndTime:     time.Now().Add(time.Hour),
		Attendees:   []string{"victim@realdomain.com"},
	}

	opts := GeneratorOptions{
		EnableICS:   true,
		ForceUnsafe: true, // Bypass domain check
		SafeDomains: cfg.SafeDomains,
	}

	_, err := GenerateICS(cfg, campaign, opts)
	if err != nil {
		t.Fatalf("Force mode should bypass domain check, got error: %v", err)
	}
}

func TestGenerateICS_DemoMode(t *testing.T) {
	cfg := &config.Config{
		ICSEnabled:  true,
		SafeDomains: []string{"example.com"},
	}

	campaign := Campaign{
		ID:          "demo-test",
		Organizer:   "sender@example.com",
		Summary:     "Demo Event",
		Description: "Original description",
		StartTime:   time.Now(),
		EndTime:     time.Now().Add(time.Hour),
		Attendees:   []string{"test@example.com"},
	}

	opts := GeneratorOptions{
		EnableICS:   true,
		DemoMode:    true,
		SafeDomains: cfg.SafeDomains,
	}

	icsData, err := GenerateICS(cfg, campaign, opts)
	if err != nil {
		t.Fatalf("Demo mode generation failed: %v", err)
	}

	icsStr := string(icsData)
	if !strings.Contains(icsStr, "DEMO ONLY") {
		t.Error("Demo mode should add DEMO ONLY prefix to description")
	}
}
