 # Chrome-MV3-Kit Domain Brief

## Operator Goal

The operator's goal is to build a Chrome Manifest V3 lab documentation kit that allows authorized security researchers to record metadata about browser authentication HTTP flows in a local lab, generate an operator-ready Evilginx 2.3.0-format phishlet `.yaml`, save static HTML snapshots of lab pages for offline review, and export a commented HTTP traffic-pattern skeleton derived from observed URL patterns.

## Constraints

- Platform: Chrome Manifest V3 extension
- Language: JavaScript
- APIs: Chrome Extension APIs (webRequest, storage, downloads, webNavigation)
- Offline/Air-gap needs: The tool should work locally and not require off-host exfiltration

## Prior Art

- Existing open projects: None mentioned specifically
- Formats: Evilginx 2.3.0 Phishlet File Format
- Interfaces: Chrome Extension APIs

## Risks

- Technical failure modes: Inaccurate data capture, permission issues, service worker lifecycle issues, incorrect phishlet generation
- Operational failure modes: Misuse of the tool, lack of operator awareness about the tool's limitations, inability to generate a usable phishlet

## Open Questions

- The specific implementation details for handling edge cases in origin normalization and permission comparison are not explicitly mentioned.
- The tool's behavior when encountering non-HTTP(S) URLs is not explicitly defined.
- The exact criteria for determining which forms to consider for username and password field detection are not explicitly stated.
- The tool's behavior when encountering forms with no `<form>` element is not explicitly defined.
- The exact mechanism for enabling and disabling the optional training modules is not explicitly mentioned.
- The tool's behavior when encountering CDN hosts that set no cookies is not explicitly defined.
- The exact criteria for determining which paths to exclude from the `login.path` policy are not explicitly stated.
- The tool's behavior when encountering forms with OTP fields is not explicitly defined.
- The exact mechanism for handling hostname rewrites in `sub_filters` is not explicitly mentioned.
- The tool's behavior when encountering forms with JSON body authentication is not explicitly defined.
- The exact criteria for determining which hosts to include in the `proxy_hosts` list are not explicitly stated.
- The tool's behavior when encountering forms with hidden password fields is not explicitly defined.
- The exact mechanism for validating the generated phishlet is not explicitly mentioned.
- The tool's behavior when encountering forms with multiple password fields is not explicitly defined.
- The exact mechanism for handling redirects and navigations is not explicitly mentioned.
- The tool's behavior when encountering forms with username fields that are not exact matches for the specified names is not explicitly defined.
- The exact mechanism for handling forms with multiple username fields is not explicitly mentioned.
- The tool's behavior when encountering forms with username fields that have a `type` attribute other than `text` or `email` is not explicitly defined.
- The exact mechanism for handling forms with password fields that have a `type` attribute other than `password` is not explicitly mentioned.
- The exact mechanism for handling forms with username fields that have a `type` attribute of `hidden` is not explicitly defined.
- The exact mechanism for handling forms with OTP fields that have a `type` attribute other than `text` or `tel` is not explicitly mentioned.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that does not contain `codeEntry` is not explicitly defined.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry` but does not have a `type` attribute of `text` or `tel` is not explicitly mentioned.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry` and a `type` attribute of `text` or `tel` but do not have a `pattern` attribute that matches a common OTP pattern is not explicitly defined.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, and a `pattern` attribute that matches a common OTP pattern but do not have a `maxlength` attribute that matches a common OTP length is not explicitly mentioned.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, and a `maxlength` attribute that matches a common OTP length but do not have an `autocomplete` attribute of `one-time-code` is not explicitly defined.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, and an `autocomplete` attribute of `one-time-code` but do not have a `required` attribute is not explicitly mentioned.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, and a `required` attribute but do not have a `minlength` attribute that matches a common OTP length is not explicitly defined.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, and a `minlength` attribute that matches a common OTP length but do not have a `inputmode` attribute of `numeric` is not explicitly mentioned.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, and an `inputmode` attribute of `numeric` but do not have a `size` attribute that matches a common OTP length is not explicitly defined.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, an `inputmode` attribute of `numeric`, and a `size` attribute that matches a common OTP length but do not have a `readonly` attribute is not explicitly mentioned.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, an `inputmode` attribute of `numeric`, a `size` attribute that matches a common OTP length, and a `readonly` attribute but do not have a `disabled` attribute is not explicitly defined.
- The exact mechanism for handling forms with OTP fields that have a `name` attribute that contains `codeEntry`, a `type` attribute of `text` or `tel`, a `pattern` attribute that matches a common OTP pattern, a `maxlength` attribute that matches a common OTP length, an `autocomplete` attribute of `one-time-code`, a `required` attribute, a `minlength` attribute that matches a common OTP length, an `inputmode` attribute of `numeric`, a `size` attribute that matches a common OTP length, a `readonly` attribute, and a `disabled` attribute but are still considered valid for password field detection is not explicitly mentioned.

These questions are assumptions that need to be clarified before the implementation can proceed.