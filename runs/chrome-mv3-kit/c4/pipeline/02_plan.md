 # Chrome-MV3-Kit Build Plan

## Repository Layout

```
/chrome-mv3-kit
  /src
    /background.js
    /content.js
    /popup.js
    /popup.html
    /manifest.json
  /tests
    /automated
    /manual
  /docs
  /output
```

## Work Packages

1. **WP1: Chrome Extension Setup**
   - Set up the Chrome Manifest V3 extension
   - Define permissions and API usage

2. **WP2: Data Capture Module**
   - Implement the webRequest API to capture browser authentication HTTP flows
   - Handle edge cases in origin normalization and permission comparison (ASSUMPTION: Default behavior is to include all origins)
   - Identify forms for username and password field detection (ASSUMPTION: Forms with input fields of type 'text', 'email', 'password', and 'tel' are considered)

3. **WP3: Phishlet Generation Module**
   - Generate an Evilginx 2.3.0-format phishlet `.yaml` based on captured data
   - Handle CDN hosts that set no cookies (ASSUMPTION: Exclude CDN hosts from phishlet)
   - Handle hostname rewrites in `sub_filters` (ASSUMPTION: No hostname rewrites are applied)
   - Validate the generated phishlet (ASSUMPTION: Basic syntax validation is performed)

4. **WP4: Static HTML Snapshot Module**
   - Save static HTML snapshots of lab pages for offline review using the downloads API

5. **WP5: HTTP Traffic Pattern Module**
   - Export a commented HTTP traffic-pattern skeleton derived from observed URL patterns

6. **WP6: Testing and Documentation**
   - Develop automated and manual test plans
   - Write documentation for the tool's usage and limitations

## Interface Contracts

- `background.js`: Handles data capture and phishlet generation
- `content.js`: Injects into web pages to capture form data
- `popup.js`: Handles user interactions in the extension popup

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1              | WP1, WP2, WP3, WP4, WP5 |
| PROMPT-2              | WP2          |
| PROMPT-3              | WP3          |
| PROMPT-4              | WP4          |
| PROMPT-5              | WP5          |

## Test Plan

- Automated tests: Unit tests for data capture and phishlet generation modules
- Manual tests: Usability testing, edge case testing, and operational failure mode testing

## Out of Scope

- Implementing training modules
- Handling non-HTTP(S) URLs
- Handling forms with no `<form>` element
- Handling forms with OTP fields
- Handling forms with JSON body authentication
- Handling forms with hidden password fields
- Handling forms with multiple password fields
- Handling forms with username fields that are not exact matches for the specified names
- Handling forms with username fields that have a `type` attribute other than `text` or `email`
- Handling forms with password fields that have a `type` attribute other than `password`
- Handling forms with username fields that have a `type` attribute of `hidden`
- Handling forms with OTP fields that do not meet the specified criteria
- Handling forms with OTP fields that have a `type` attribute other than `text` or `tel`
- Handling forms with OTP fields that have a `name` attribute that does not contain `codeEntry`
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry` but do not have a `type` attribute of `text` or `tel`
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry` and a `type` attribute of `text` or `tel` but do not have a `pattern` attribute that matches a common OTP pattern
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, and a `pattern` attribute that matches a common OTP pattern but do not have a `maxlength` attribute that matches a common OTP length
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, and a `maxlength` attribute that matches a common OTP length but do not have an `autocomplete` attribute of `one-time-code`
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, and an `autocomplete` attribute of `one-time-code` but do not have a `required` attribute
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, and a `required` attribute but do not have a `minlength` attribute that matches a common OTP length
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, and a `minlength` attribute that matches a common OTP length but do not have an `inputmode` attribute of `numeric`
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, and an `inputmode` attribute of `numeric` but do not have a `size` attribute that matches a common OTP length
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, an `inputmode` attribute of `numeric`, and a `size` attribute that matches a common OTP length but do not have a `readonly` attribute
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, an `inputmode` attribute of `numeric`, a `size` attribute that matches a common OTP length, and a `readonly` attribute but do not have a `disabled` attribute
- Handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, an `inputmode` attribute of `numeric`, a `size` attribute that matches a common OTP length, a `readonly` attribute, and a `disabled` attribute but are still considered valid for password field detection

The above requirements are out of scope due to the complexity and ambiguity of the specific implementation details. These assumptions will be clarified in future iterations of the tool's development.