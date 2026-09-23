 ## Implementation Tree

   - `/gophish-ics`
     - `main.go`
     - `config.go`
     - `email.go`
     - `ics.go`
     - `telemetry.go`
   - `/gophish-api`
     - `client.go`
   - `/tests`
     - `/unit`
     - `/integration`
     - `/acceptance`
   - `/docs`
     - `README.md`
     - `API.md`

   ## Implementation Details

   ### FILE: src/gophish-ics/main.go

   ```python
   package main

   import (
       "fmt"
       "gophish-ics/src/gophish-api"
       "gophish-ics/src/gophish-ics"
   )

   func main() {
       // Load configuration
       config := gophish_ics.LoadConfig()

       // Initialize GoPhish API client
       client := gophish_api.NewClient(config.GoPhishAPIURL, config.GoPhishAPIKey)

       // Generate email content
       emailContent := gophish_ics.GenerateEmailContent(config.EmailTemplate)

       // Generate ICS content
       icsContent := gophish_ics.GenerateICSContent(emailContent)

       // Send email with ICS attachment
       err := client.SendEmail(config.EmailFrom, config.EmailTo, config.EmailSubject, emailContent, icsContent)
       if err != nil {
           fmt.Println("Error sending email:", err)
           return
       }

       // Collect telemetry
       go gophish_ics.CollectTelemetry(config.TelemetryStore)
   }
   ```

   ### FILE: src/gophish-ics/config.go

   ```python
   package gophish_ics

   import (
       "encoding/json"
       "io/ioutil"
   )

   type Config struct {
       GoPhishAPIURL string `json:"gophish_api_url"`
       GoPhishAPIKey string `json:"gophish_api_key"`
       EmailTemplate string `json:"email_template"`
       EmailFrom     string `json:"email_from"`
       EmailTo       string `json:"email_to"`
       EmailSubject  string `json:"email_subject"`
       TelemetryStore string `json:"telemetry_store"`
   }

   func LoadConfig() Config {
       data, err := ioutil.ReadFile("config.json")
       if err != nil {
           panic(err)
       }

       var config Config
       err = json.Unmarshal(data, &config)
       if err != nil {
           panic(err)
       }

       return config
   }
   ```

   ### FILE: src/gophish-ics/email.go

   ```python
   package gophish_ics

   import (
       "bytes"
       "text/template"
   )

   func GenerateEmailContent(templatePath string) string {
       tmpl, err := template.ParseFiles(templatePath)
       if err != nil {
           panic(err)
       }

       var buf bytes.Buffer
       err = tmpl.Execute(&buf, nil)
       if err != nil {
           panic(err)
       }

       return buf.String()
   }
   ```

   ### FILE: src/gophish-ics/ics.go

   ```python
   package gophish_ics

   import (
       "github.com/arran4/golang-ical"
   )

   func GenerateICSContent(emailContent string) string {
       // Extract event details from email content
       // Create iCalendar object
       // Add event details to iCalendar object
       // Return iCalendar object as string
   }
   ```

   ### FILE: src/gophish-ics/telemetry.go

   ```python
   package gophish_ics

   import (
       "fmt"
       "time"
   )

   func CollectTelemetry(storePath string) {
       // Open telemetry store
       // Collect telemetry data
       // Write telemetry data to store
       // Repeat every X minutes
   }
   ```

   ### FILE: src/gophish-api/client.go

   ```python
   package gophish_api

   import (
       "bytes"
       "encoding/json"
       "net/http"
   )

   type Client struct {
       apiURL string
       apiKey string
   }

   func NewClient(apiURL, apiKey string) *Client {
       return &Client{apiURL, apiKey}
   }

   func (c *Client) SendEmail(from, to, subject, body, icsContent string) error {
       // Create email object
       // Send email using GoPhish API
       // Return error if any
   }
   ```

   ### FILE: docs/README.md

   ```markdown
   # gophish-ics

   gophish-ics is a tool that augments or wraps GoPhish-style phishing campaign workflows. It enables authorized operators to deliver ICS/calendar invite style messages, collect RSVP/calendar response telemetry, and maintain lab safety defaults.

   ## Usage

   ...

   ## Safety Defaults

   ...

   ## Authorized Use

   This tool is intended for authorized use only. Unauthorized use is prohibited.
   ```

   ### FILE: docs/API.md

   ```markdown
   # gophish-ics API

   gophish-ics provides a RESTful API for programmatic interaction.

   ## Endpoints

   ...
   ```

   ## Build Notes

   - The ICS content generation module is not fully implemented. The extraction of event details from email content and the creation of iCalendar objects are not implemented.
   - The telemetry collection module is not fully implemented. The opening of the telemetry store, the collection of telemetry data, and the writing of telemetry data to the store are not implemented.
   - The GoPhish API client module is not fully implemented. The creation of email objects and the sending of emails using the GoPhish API are not implemented.
   - The documentation is not fully implemented. The usage, safety defaults, and API sections are not fully documented.
   - The tool does not have a command-line interface.
   - The tool does not have a configuration file.
   - The tool does not have a dry-run mode.
   - The tool does not have an allowlist of email addresses that it can send emails to.
   - The tool does not require explicit confirmation from the operator before sending emails or modifying the GoPhish server.
   - The tool does not handle network failures and API errors gracefully.
   - The tool does not have a section on operational constraints and safety defaults in the documentation.
   - The tool does not have a section on degradation modes in the documentation.
   - The tool does not have a section on secrets handling methods in the documentation.
   - The tool does not have a section on operator workflow in the documentation.

   To run scanners, use the following commands:

   ```
   semgrep --config auto src/gophish-ics
   ast-grep -r '^import\s+.*\bos\b' src/gophish-ics
   ```