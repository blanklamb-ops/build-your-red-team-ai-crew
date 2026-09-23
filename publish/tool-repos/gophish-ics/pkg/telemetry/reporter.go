package telemetry

import "fmt"

// GenerateCampaignReport generates an aggregated RSVP report for a campaign
func GenerateCampaignReport(campaignID string, totalSent int, store RSVPStore) (*Report, error) {
	events, err := store.GetResponses(campaignID)
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve RSVP events: %w", err)
	}

	report := &Report{
		CampaignID: campaignID,
		TotalSent:  totalSent,
	}

	// Aggregate counts by status
	for _, event := range events {
		switch event.Status {
		case StatusAccept:
			report.AcceptCount++
		case StatusDecline:
			report.DeclineCount++
		case StatusTentative:
			report.TentativeCount++
		case StatusNone:
			// Don't count explicit "none" responses
		}
	}

	// Calculate no-response count
	totalResponses := report.AcceptCount + report.DeclineCount + report.TentativeCount
	report.NoResponseCount = report.TotalSent - totalResponses
	if report.NoResponseCount < 0 {
		report.NoResponseCount = 0
	}

	return report, nil
}
