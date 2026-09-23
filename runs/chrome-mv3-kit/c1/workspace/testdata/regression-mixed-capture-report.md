# Lab Capture Report

**Session ID:** 00000000-0000-4000-8000-000000000001  
**Started:** 2026-09-04T12:00:00.000Z  
**Stopped:** 2026-09-04T12:04:00.000Z  
**Coverage:** COMPLETE


## Captured Events

Total: 20 events

### Event 1
- **URL:** https://login.idp.test/consumers/oauth2/v2.0/authorize
- **Method:** GET
- **Status:** 200
- **Source:** webRequest
- **Set-Cookie names:** fpc, stsservicecookie

### Event 2
- **URL:** https://login.idp.test/common/GetCredentialType
- **Method:** POST
- **Status:** 200
- **Source:** webRequest

### Event 3
- **URL:** https://login.wallet.test/login.srf
- **Method:** GET
- **Status:** 200
- **Source:** webRequest
- **Set-Cookie names:** MSPRequ, uaid
- **Form fields captured:** 2 form(s)
  - Form 1: action=https://login.wallet.test/consumers/savestate
    - LoginOptions (hidden)
    - NewUser (hidden)
  - Form 2: action=https://login.wallet.test/ppsecure/post.srf
    - loginfmt (hidden)
    - passwd (password)
    - PPFT (hidden)

### Event 4
- **URL:** https://login.wallet.test/ppsecure/post.srf
- **Method:** POST
- **Status:** 302
- **Source:** webRequest
- **Set-Cookie names:** MSPAuth, MSPProf

### Event 5
- **URL:** https://login.wallet.test/checkpassword.srf
- **Method:** POST
- **Status:** 200
- **Source:** webRequest

### Event 6
- **URL:** https://login.wallet.test/consumers/savestate
- **Method:** POST
- **Status:** 200
- **Source:** webRequest

### Event 7
- **URL:** https://login.wallet.test/auth/complete-silent-signin
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 8
- **URL:** https://assets.authcdn.test/shared/js/login.js
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 9
- **URL:** https://account.corp.test/account/home
- **Method:** GET
- **Status:** 200
- **Source:** webRequest
- **Set-Cookie names:** MSPVis, x-portal-routekey

### Event 10
- **URL:** https://graph.idp.test/v1.0/me
- **Method:** GET
- **Status:** 200
- **Source:** webRequest
- **Set-Cookie names:** api_session

### Event 11
- **URL:** https://admin.corp.test/admin
- **Method:** GET
- **Status:** 200
- **Source:** webRequest
- **Set-Cookie names:** admin_session

### Event 12
- **URL:** https://monitor.metrics.test/ingest
- **Method:** POST
- **Status:** 204
- **Source:** webRequest

### Event 13
- **URL:** https://wcpstatic.cdn.test/assets/app.js
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 14
- **URL:** https://uhf-exp-fd-gbcrdgggfbggh0g3.b02.edgecdn.test/uhf/header.js
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 15
- **URL:** https://storage.blob.test/container/file
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 16
- **URL:** https://amcdn.static.test/amcdn/x
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 17
- **URL:** https://fpt.wallet.test/fpt/collect
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 18
- **URL:** https://copilot.idp.test/
- **Method:** GET
- **Status:** 200
- **Source:** webRequest
- **Set-Cookie names:** fpc

### Event 19
- **URL:** https://events.clarity.ms/collect
- **Method:** GET
- **Status:** 200
- **Source:** webRequest

### Event 20
- **URL:** https://browser.events.data.idp.test/OneCollector/1.0/
- **Method:** POST
- **Status:** 204
- **Source:** webRequest
