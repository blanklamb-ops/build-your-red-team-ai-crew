package ics

import (
	"fmt"
	"strings"

	ics "github.com/arran4/golang-ical"
	"github.com/research/gophish-ics/pkg/config"
)

// GeneratorOptions holds options for ICS generation
type GeneratorOptions struct {
	EnableICS    bool
	ForceUnsafe  bool
	DemoMode     bool
	SafeDomains  []string
}

// GenerateICS generates an RFC 5545 compliant iCalendar invite
func GenerateICS(cfg *config.Config, campaign Campaign, opts GeneratorOptions) ([]byte, error) {
	// Safety check: respect config flag unless explicitly overridden
	if !opts.EnableICS && !cfg.ICSEnabled {
		return nil, fmt.Errorf("ICS generation is disabled by default for safety. " +
			"To enable: edit config/config.yaml OR use --enable-ics flag")
	}

	// Validate required fields
	if err := validateCampaign(campaign); err != nil {
		return nil, fmt.Errorf("invalid campaign data: %w", err)
	}

	// Domain safety check (unless --force)
	if !opts.ForceUnsafe {
		if err := validateDomains(campaign.Attendees, cfg.SafeDomains); err != nil {
			return nil, fmt.Errorf("unsafe email domains detected: %w\nUse --force to bypass (authorized engagements only)", err)
		}
	}

	// Create calendar
	cal := ics.NewCalendar()
	cal.SetMethod(ics.MethodRequest) // REQUEST = invitation
	cal.SetProductId("-//gophish-ics//NONSGML v1.0//EN")

	// Create event
	event := cal.AddEvent(campaign.ID)
	event.SetSummary(campaign.Summary)

	// Add demo mode indicator if enabled
	description := campaign.Description
	if opts.DemoMode {
		description = "[DEMO ONLY - NOT FOR OPERATIONAL USE]\n\n" + description
	}
	event.SetDescription(description)

	event.SetStartAt(campaign.StartTime)
	event.SetEndAt(campaign.EndTime)

	if campaign.Location != "" {
		event.SetLocation(campaign.Location)
	}

	// Set organizer
	event.SetOrganizer(campaign.Organizer, ics.WithCN(campaign.Summary))

	// Add attendees with NEEDS-ACTION status
	for _, attendee := range campaign.Attendees {
		event.AddAttendee(attendee,
			ics.CalendarUserTypeIndividual,
			ics.ParticipationStatusNeedsAction,
			ics.ParticipationRoleReqParticipant,
			ics.WithRSVP(true))
	}

	return []byte(cal.Serialize()), nil
}

func validateCampaign(c Campaign) error {
	if c.ID == "" {
		return fmt.Errorf("campaign ID is required")
	}
	if c.Organizer == "" {
		return fmt.Errorf("organizer email is required")
	}
	if c.Summary == "" {
		return fmt.Errorf("event summary is required")
	}
	if c.StartTime.IsZero() {
		return fmt.Errorf("start time is required")
	}
	if c.EndTime.IsZero() {
		return fmt.Errorf("end time is required")
	}
	if c.EndTime.Before(c.StartTime) {
		return fmt.Errorf("end time must be after start time")
	}
	if len(c.Attendees) == 0 {
		return fmt.Errorf("at least one attendee is required")
	}
	return nil
}

func validateDomains(emails []string, safeDomains []string) error {
	var unsafeDomains []string

	for _, email := range emails {
		domain := extractDomain(email)
		if !isAllowedDomain(domain, safeDomains) {
			unsafeDomains = append(unsafeDomains, domain)
		}
	}

	if len(unsafeDomains) > 0 {
		return fmt.Errorf("unsafe domains: %v", unique(unsafeDomains))
	}

	return nil
}

func extractDomain(email string) string {
	parts := strings.Split(email, "@")
	if len(parts) != 2 {
		return ""
	}
	return strings.ToLower(parts[1])
}

func isAllowedDomain(domain string, safeDomains []string) bool {
	for _, safe := range safeDomains {
		if strings.HasSuffix(domain, safe) {
			return true
		}
	}
	return false
}

func unique(items []string) []string {
	seen := make(map[string]bool)
	var result []string
	for _, item := range items {
		if !seen[item] {
			seen[item] = true
			result = append(result, item)
		}
	}
	return result
}
