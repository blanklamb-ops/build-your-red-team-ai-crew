package config

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

// Config represents the application configuration
type Config struct {
	ICSEnabled      bool     `yaml:"ics_enabled"`
	SafeDomains     []string `yaml:"safe_domains"`
	DefaultTimezone string   `yaml:"default_timezone"`
	DatabasePath    string   `yaml:"database_path"`
}

// LoadConfig loads configuration from the specified YAML file
func LoadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w\nExample config:\n%s", err, exampleConfig())
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("failed to parse config YAML: %w", err)
	}

	// Set defaults
	if cfg.DefaultTimezone == "" {
		cfg.DefaultTimezone = "UTC"
	}
	if cfg.DatabasePath == "" {
		cfg.DatabasePath = "./telemetry.db"
	}
	if len(cfg.SafeDomains) == 0 {
		cfg.SafeDomains = []string{"example.com", "example.org", "example.net", "test.invalid"}
	}

	return &cfg, nil
}

func exampleConfig() string {
	return `ics_enabled: false
safe_domains:
  - example.com
  - example.org
  - example.net
  - test.invalid
default_timezone: UTC
database_path: ./telemetry.db
`
}
