package config

import (
	"os"
	"path/filepath"
	"testing"
)

// TestDefaultConfigIsDisabled validates that the shipped config has ICS disabled
// This is a CRITICAL safety test per acceptance criteria A6
func TestDefaultConfigIsDisabled(t *testing.T) {
	// Load the actual checked-in config file
	configPath := filepath.Join("..", "..", "config", "config.yaml")

	cfg, err := LoadConfig(configPath)
	if err != nil {
		t.Fatalf("Failed to load default config: %v", err)
	}

	if cfg.ICSEnabled {
		t.Fatal("SAFETY VIOLATION: Default config has ics_enabled: true. " +
			"The checked-in config MUST have ics_enabled: false for lab safety.")
	}
}

func TestLoadConfig_MissingFile(t *testing.T) {
	_, err := LoadConfig("/nonexistent/config.yaml")
	if err == nil {
		t.Fatal("Expected error for missing config file")
	}
}

func TestLoadConfig_ValidConfig(t *testing.T) {
	// Create temporary config
	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "test-config.yaml")

	content := `ics_enabled: true
safe_domains:
  - test.local
default_timezone: America/New_York
database_path: /tmp/test.db
`

	if err := os.WriteFile(configPath, []byte(content), 0600); err != nil {
		t.Fatalf("Failed to write test config: %v", err)
	}

	cfg, err := LoadConfig(configPath)
	if err != nil {
		t.Fatalf("LoadConfig failed: %v", err)
	}

	if !cfg.ICSEnabled {
		t.Error("Expected ICSEnabled to be true")
	}
	if cfg.DefaultTimezone != "America/New_York" {
		t.Errorf("Got timezone %s, want America/New_York", cfg.DefaultTimezone)
	}
	if len(cfg.SafeDomains) != 1 || cfg.SafeDomains[0] != "test.local" {
		t.Errorf("Safe domains mismatch: %v", cfg.SafeDomains)
	}
}
