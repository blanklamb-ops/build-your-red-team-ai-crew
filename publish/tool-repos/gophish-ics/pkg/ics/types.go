package ics

import "time"

// Campaign represents a phishing campaign with calendar invite details
type Campaign struct {
	ID          string    `json:"id"`
	Organizer   string    `json:"organizer"`    // email address
	Summary     string    `json:"summary"`      // event title
	Description string    `json:"description"`  // event body
	StartTime   time.Time `json:"start_time"`   // explicit timezone
	EndTime     time.Time `json:"end_time"`
	Attendees   []string  `json:"attendees"`    // recipient emails
	Location    string    `json:"location"`     // optional meeting location
}
