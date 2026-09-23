package telemetry

import "time"

// ResponseStatus represents the RSVP status of a recipient
type ResponseStatus int

const (
	StatusNone ResponseStatus = iota
	StatusAccept
	StatusDecline
	StatusTentative
)

func (s ResponseStatus) String() string {
	switch s {
	case StatusNone:
		return "none"
	case StatusAccept:
		return "accept"
	case StatusDecline:
		return "decline"
	case StatusTentative:
		return "tentative"
	default:
		return "unknown"
	}
}

// ParseResponseStatus converts a string to ResponseStatus
func ParseResponseStatus(s string) ResponseStatus {
	switch s {
	case "accept", "accepted":
		return StatusAccept
	case "decline", "declined":
		return StatusDecline
	case "tentative":
		return StatusTentative
	default:
		return StatusNone
	}
}

// RSVPEvent represents a single RSVP response from a recipient
type RSVPEvent struct {
	ID          int64          `json:"id"`
	RecipientID string         `json:"recipient_id"`
	CampaignID  string         `json:"campaign_id"`
	Status      ResponseStatus `json:"status"`
	Timestamp   time.Time      `json:"timestamp"`
}

// Report contains aggregated RSVP statistics for a campaign
type Report struct {
	CampaignID      string `json:"campaign_id"`
	TotalSent       int    `json:"total_sent"`
	AcceptCount     int    `json:"accept_count"`
	DeclineCount    int    `json:"decline_count"`
	TentativeCount  int    `json:"tentative_count"`
	NoResponseCount int    `json:"no_response_count"`
}
