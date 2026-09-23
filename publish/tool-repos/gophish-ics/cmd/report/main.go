package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"text/tabwriter"

	"github.com/research/gophish-ics/pkg/telemetry"
)

func main() {
	dbPath := flag.String("db-path", "./telemetry.db", "Path to telemetry database")
	campaignID := flag.String("campaign-id", "", "Campaign ID to report on (required)")
	totalSent := flag.Int("total-sent", 0, "Total emails sent (required for accurate no-response count)")
	formatJSON := flag.Bool("json", false, "Output report as JSON")

	flag.Parse()

	if *campaignID == "" {
		fmt.Fprintln(os.Stderr, "Error: --campaign-id is required")
		flag.Usage()
		os.Exit(1)
	}

	// Open telemetry store
	store, err := telemetry.NewSQLiteStore(*dbPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open telemetry database: %v\n", err)
		os.Exit(1)
	}
	defer store.Close()

	// Generate report
	report, err := telemetry.GenerateCampaignReport(*campaignID, *totalSent, store)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to generate report: %v\n", err)
		os.Exit(1)
	}

	// Output report
	if *formatJSON {
		jsonData, err := json.MarshalIndent(report, "", "  ")
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to marshal JSON: %v\n", err)
			os.Exit(1)
		}
		fmt.Println(string(jsonData))
	} else {
		// Table format
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
		fmt.Fprintf(w, "Campaign RSVP Report\n")
		fmt.Fprintf(w, "====================\n")
		fmt.Fprintf(w, "Campaign ID:\t%s\n", report.CampaignID)
		fmt.Fprintf(w, "Total Sent:\t%d\n", report.TotalSent)
		fmt.Fprintf(w, "\n")
		fmt.Fprintf(w, "Accepted:\t%d\n", report.AcceptCount)
		fmt.Fprintf(w, "Declined:\t%d\n", report.DeclineCount)
		fmt.Fprintf(w, "Tentative:\t%d\n", report.TentativeCount)
		fmt.Fprintf(w, "No Response:\t%d\n", report.NoResponseCount)
		w.Flush()
	}
}
