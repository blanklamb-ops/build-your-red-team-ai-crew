package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/research/gophish-ics/pkg/config"
	"github.com/research/gophish-ics/pkg/ics"
)

func main() {
	configPath := flag.String("config", "config/config.yaml", "Path to configuration file")
	inputPath := flag.String("input", "", "Path to campaign JSON file (required)")
	outputPath := flag.String("output", "", "Output path for .ics file (stdout if empty)")
	enableICS := flag.Bool("enable-ics", false, "Override config to enable ICS generation")
	force := flag.Bool("force", false, "Bypass domain safety checks (authorized engagements only)")
	demo := flag.Bool("demo", false, "Add demo mode notice to ICS description")

	flag.Parse()

	if *inputPath == "" {
		fmt.Fprintln(os.Stderr, "Error: --input is required")
		flag.Usage()
		os.Exit(1)
	}

	// Load configuration
	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Configuration error: %v\n", err)
		os.Exit(1)
	}

	// Load campaign data
	campaignData, err := os.ReadFile(*inputPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read campaign file: %v\n", err)
		os.Exit(1)
	}

	var campaign ics.Campaign
	if err := json.Unmarshal(campaignData, &campaign); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to parse campaign JSON: %v\n", err)
		os.Exit(1)
	}

	// Generate ICS
	opts := ics.GeneratorOptions{
		EnableICS:   *enableICS,
		ForceUnsafe: *force,
		DemoMode:    *demo,
		SafeDomains: cfg.SafeDomains,
	}

	icsData, err := ics.GenerateICS(cfg, campaign, opts)
	if err != nil {
		fmt.Fprintf(os.Stderr, "ICS generation failed: %v\n", err)
		os.Exit(1)
	}

	// Write output
	if *outputPath == "" {
		// Write to stdout
		fmt.Print(string(icsData))
	} else {
		// Create output directory if needed
		if err := os.MkdirAll("output", 0755); err != nil {
			fmt.Fprintf(os.Stderr, "Failed to create output directory: %v\n", err)
			os.Exit(1)
		}

		if err := os.WriteFile(*outputPath, icsData, 0644); err != nil {
			fmt.Fprintf(os.Stderr, "Failed to write ICS file: %v\n", err)
			os.Exit(1)
		}

		fmt.Fprintf(os.Stderr, "ICS file generated: %s\n", *outputPath)
	}
}
