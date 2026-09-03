# Authentication — obtaining a session token

Reference for the Integration department. This document describes **how the Smartup SFA (trade)
mobile app authenticates and what it gets back**, up to and including the `token` that every
subsequent call (including `sync:sync`, see
[`tvt_save_person_visit.md`](./tvt_save_person_visit.md)) requires.

Everything below is derived from the app source:

| What | Where in the app |
|---|---|
| Endpoint constants | `smartup5x_account/lib/network/network_manager.dart` |
| Login flow (password) | `smartup5x_account/lib/bloc/login/login_account.dart` → `requestOAuth()` |
| Login flow (OTP / SMS) | `smartup5x_account/lib/bloc/phone/phone_account.dart` |
| `account_code` / password hashing | `smartup5x_account/lib/bean/account.dart`, `.../common/util.dart` |
| Device fingerprint | `smartup5x_account/lib/common/version_helper.dart`, `.../pref/login_pref.dart` |
| Session info parsing | `smartup5x_account/lib/pref/account_pref.dart` → `saveUserInfos()` |
| HTTP layer | `gwslib/lib/network/network.dart` |

---

## 1. The flow at a glance

```
                    ┌──────────────────────────────────────────┐
                    │ You already know: server_url, project_code│
                    └──────────────────────────────────────────┘
                                      │
             ┌────────────────────────┴────────────────────────┐
             │                                                 │
   PASSWORD FLOW (used by the app)                    OTP / SMS FLOW (alternative)
             │                                                 │
             │                                   1. m$get_company_infos_by_phone
             │                                      → list of companies for the phone
             │                                                 │
             │                                   2. m$gen_onetime_password
             │                                      → { token, expires_in }, SMS is sent
             │                                                 │
   1. s:log_in_device                             3. s:logon_device_by_otp
      login + password_hash + account_code           otp_token + otp + device info
      + device fingerprint                                     │
             │                                                 │
             └────────────────────┬────────────────────────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │  token  (session token)  │
                    └──────────────────────────┘
                                  │
                    2. m:session_info_mobile   (GET, token header)
                       → user profile + projects + filials + translations
                                  │
                                  ▼
                    Pick a filial_id for project_code = "trade"
                                  │
                                  ▼
                    3. mt/sync:sync  and every other business call
                       headers: token, project_code, filial_id
```

The password flow is what the trade app uses by default. Both flows end at the same place: a
`token` string.

---

## 2. Prerequisites

| Value | Where it comes from | Example |
|---|---|---|
| `server_url` | Chosen by the user in the app, or hard-coded per deployment. Production is `https://smartup.online`. A trailing `/` is stripped before use. | `https://smartup.online` |
| `project_code` | Constant per app. The trade app reports `"trade"` (`TradeApp.supportedProjectCodes()`). | `trade` |
| `login` | User login. **Must contain `@`**, in the form `user@company_code`; the app rejects a login without a non-empty part after `@`. | `zarif@greenwhite` |
| `password` | Plain password — hashed before sending, see 3.2. | — |

### HTTP conventions

* All calls are `POST` unless stated otherwise, with `Content-Type: application/json`.
* The body is a JSON object (or a JSON array for `logon_device_by_otp`).
* Paths are appended to `server_url` with exactly one `/` between them.
* Note the `$` in some route names (`m$gen_onetime_password`) — it is a literal character in the
  URL, not a variable.

---

## 3. Step 1 (password flow) — `log_in_device`

```
POST {server_url}/b/biruni/s:log_in_device
Content-Type: application/json
```

Headers:

| Header | Required | Description |
|---|---|---|
| `project_code` | conditional | Sent only when the app has a project code. Always send `trade`. |

### 3.1 Request body

```json
{
  "login": "zarif@greenwhite",
  "password_hash": "8843d7f92416211de9ebb963ff4ce28125932878",
  "account_code": "5f4dcc3b5aa765d61d8327deb882cf99...",
  "device_name": "SM-A325F",
  "device_code": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "device_version": "13",
  "device_sdk": "33",
  "version_code": "1042",
  "version_name": "1.4.2",
  "device_kind": "A"
}
```

| Field | Type | Req. | Description |
|---|---|---|---|
| `login` | string | yes | Trimmed user login, `user@company_code`. |
| `password_hash` | string | yes | **SHA-1 of the plain password, hex, lowercase.** See 3.2. |
| `account_code` | string | yes | Stable client-side account id. See 3.3. |
| `device_name` | string | yes | Device model. Android: `Build.MODEL`. iOS: `utsname.machine`. |
| `device_code` | string | yes | **Persistent device UUID.** Generated once as a UUID v1 and stored on the device forever. Huawei builds append the suffix `-hmc`. This is the device identity the server registers — see 7.3. |
| `device_version` | string | yes | OS release. Android: `Build.VERSION.RELEASE`. iOS: `utsname.release`. |
| `device_sdk` | string | yes | Android: `Build.VERSION.SDK_INT`. iOS: first 20 chars of `utsname.version`. |
| `version_code` | string | yes | App build number. |
| `version_name` | string | yes | App version name. |
| `device_kind` | string | yes | `A` = Android (Google flavor), `H` = Android (Huawei flavor), `I` = iOS. |

The seven `device_*` / `version_*` fields come from `DeviceInfoHelperImpl.mapDeviceInfo()`. An
integration job that is not a real device should still send plausible, **stable** values — in
particular `device_code` must not change between runs, or the server will see a new device each
time.

### 3.2 `password_hash`

```
password_hash = lowercase_hex( SHA1( utf8(password) ) )
```

From `StringImageUrl.calcSha1()`:

```dart
String calcSha1() {
  final data = utf8.encode(this);
  return sha1.convert(data).toString().toLowerCase();
}
```

No salt, no iteration count. The plain password never leaves the device.

### 3.3 `account_code`

```
account_code = lowercase_hex( SHA256( utf8( login + "#" + server_url_without_trailing_slash ) ) )
```

From `Server.genServerId()`:

```dart
static String genServerId(String login, String serverUrl) {
  final data = utf8.encode("$login#${fixServerUrl(serverUrl)}");
  return sha256.convert(data).toString().toLowerCase();
}
```

`fixServerUrl` only strips one trailing `/`. Example: for
`login = "zarif@greenwhite"` and `server_url = "https://smartup.online/"`, the hashed string is
`zarif@greenwhite#https://smartup.online`.

It is a deterministic local identifier for the (login, server) pair — the same input always
produces the same `account_code`. The app reuses a previously stored one when re-authenticating an
existing account, otherwise it regenerates it with this formula.

### 3.4 Response

`200 OK`, JSON object. The app reads four fields:

| Field | Type | Description |
|---|---|---|
| `token` | string | **The session token.** Put it in the `token` header of every subsequent call. |
| `user_id` | int \| string | Server user id. The app parses it leniently — it may arrive as a number or a string. |
| `user_name` | string | Display name of the user. |
| `company_name` | string | Company/tenant display name. |

Other fields may be present; the app ignores them.

Example:

```json
{
  "token": "eyJhbGciOi...",
  "user_id": "42",
  "user_name": "Zarif Ergashev",
  "company_name": "Green White"
}
```

At this point you have a token, but **not yet a `filial_id`** — that comes from step 2.

---

## 4. Alternative — OTP / SMS flow

Used when the user logs in by phone number instead of login+password. Three calls.

### 4.1 Find the companies for a phone number

```
POST {server_url}/b/biruni/m$get_company_infos_by_phone
headers: lang_code, project_code
body: { "phone": "998901234567", "lang_code": "ru" }
```

Response: array of `{ "name": ..., "code": ... }`. `code` is the **company code** needed by the next
call. When exactly one company is returned the app uses it automatically; when several are returned
the user picks one.

The phone is sent as country code + number concatenated, digits only, at least 10 digits.

### 4.2 Request the one-time password

```
POST {server_url}/b/biruni/m$gen_onetime_password
headers: lang_code, project_code
body: { "code": "<company_code>", "phone": "998901234567", "lang_code": "ru" }
```

Response:

| Field | Type | Description |
|---|---|---|
| `token` | string | **OTP transaction token** — not a session token. Passed back in 4.3. |
| `expires_in` | int | Validity of the OTP in seconds. The app falls back to `120` when the field is missing or unparsable. |

The SMS with the 6-digit code is sent by the server as a side effect.

### 4.3 Exchange the OTP for a session token

```
POST {server_url}/b/biruni/s:logon_device_by_otp
headers: project_code
```

**The body is a positional JSON array**, not an object:

```json
[
  "<otp_token from 4.2>",
  "<otp typed by the user>",
  "",
  "SM-A325F",
  "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "13",
  "33",
  "1042",
  "1.4.2",
  "A",
  "<account_code>"
]
```

| Index | Value |
|---|---|
| 0 | OTP transaction token from 4.2 |
| 1 | The OTP code |
| 2 | Empty string (reserved) |
| 3 | `device_name` |
| 4 | `device_code` (persistent UUID) |
| 5 | `device_version` |
| 6 | `device_sdk` |
| 7 | `version_code` |
| 8 | `version_name` |
| 9 | `device_kind` (`A`/`H`/`I`) |
| 10 | `account_code` |

Indices 3–9 are `DeviceInfoHelperImpl.listDeviceInfo()` in order — the same seven values as the map
in 3.1, but positional. On iOS index 3 has `,` replaced with `.` in the machine name.

Here `account_code` is `SHA256(phone + "#" + server_url)` — the **phone**, not a login, is hashed.

**The response is also a positional JSON array:**

```json
["42", "Zarif Ergashev", "eyJhbGciOi..."]
```

| Index | Value |
|---|---|
| 0 | `user_id` (string) |
| 1 | `user_name` |
| 2 | **`token`** |

---

## 5. Step 2 — `session_info_mobile`: profile, projects and filials

The token alone is not enough to call business methods: every one of them also needs a `filial_id`.
This call is where the app learns which filials the user has.

```
GET {server_url}/b/biruni/m:session_info_mobile
headers:
  token:     <session token>
  lang_code: ru | en | uz
```

**The response is a positional JSON array** (`UserInfo.fromJson`):

| Index | Field | Type | Description |
|---|---|---|---|
| 0 | `user_name` | string | Display name. |
| 1 | `gender` | string | `M` / `F`. |
| 2 | `photo_sha` | string | SHA of the avatar image; download separately via the file routes. |
| 3 | `password_policy` | array | `[enable, change_on, change_required, temp_period, strength]`. When `change_required` is set the app forces a password change before letting the user in. |
| 4 | `projects` | array | **The filial list, per project.** See below. |
| 5 | `translate_ru` | array | UI translations. Irrelevant for integration. |
| 6 | `translate_en` | array | Optional. Irrelevant for integration. |
| 7 | `company_name` | string | Optional; defaults to `"Unknown"`. |
| 8 | `translate_uz` | array | Optional. Irrelevant for integration. |
| 9 | `languages` | array | Optional. `[[lang_code, lang_name, translates], ...]`. |

### `projects` (index 4)

Each element is itself positional:

| Index | Value |
|---|---|
| 0 | `project_code` — e.g. `"trade"` |
| 1 | (project name — the app does not read it) |
| 2 | array of filials, each `[filial_id, filial_name]` |

Example:

```json
[
  ["trade", "Smartup Trade", [["1", "Head office"], ["7", "Samarkand branch"]]],
  ["anor",  "Smartup Anor",  [["1", "Head office"]]]
]
```

`filial_id` arrives as a **string** and is parsed to an int by the app.

For a trade integration job: take the element whose `project_code == "trade"` and pick the
`filial_id` you want to push visits into.

---

## 6. Step 3 — using the token

Every subsequent business call carries these headers:

| Header | Value |
|---|---|
| `token` | The session token from step 1. |
| `project_code` | `trade` |
| `filial_id` | The chosen filial id, as a string. |
| `timezone_code` | Optional, IANA id — sent by the sync call, e.g. `Asia/Tashkent`. |
| `lang_code` | Optional, for calls that return localized text. |

Note the header is literally named **`token`** — not `Authorization`, no `Bearer` prefix.

---

## 7. Errors

### 7.1 HTTP statuses the app handles explicitly

| Status | Meaning | App behaviour |
|---|---|---|
| `401` | Token invalid or expired. | The stored server record is marked `isExpired = true` and the user is sent back to the login screen. |
| `403` | Route refused — the user/role has no access to this route. | Shows "route refused". |
| `429` | Too many login attempts. Response carries a `Retry-After` header, in **seconds**. | Shows a "try again in H:M:S" message. **An integration job must honour `Retry-After` and back off**, otherwise the account gets locked out further. |

### 7.2 Error texts that carry meaning

The server may return `200` with an error body, or a `4xx` whose body is a plain message. The app
pattern-matches on these:

| Text fragment | Meaning |
|---|---|
| `no data found` | Wrong login or password. |
| `ROUTE: Unauthenticated` | The token is not (or no longer) valid. Same handling as `401`. |
| `Вы вошли в систему с незарегистрированного устройства` / `unregistered device` | The `device_code` is not registered for this account. Re-run `log_in_device` with the **same** `device_code`. |
| `Требуется авторизация. Пожалуйста, войдите в систему` | Session expired; re-authenticate. |

These are matched by the sync layer (`sync_protocol.dart`) as well as the login layer, because a
token can go stale in the middle of a sync.

### 7.3 Device registration

`log_in_device` / `logon_device_by_otp` both register the device fingerprint against the account.
The server can then reject calls coming from an unknown `device_code`. Practical consequences for an
integration job:

* Generate `device_code` **once** and persist it. Do not generate a UUID per run.
* Keep `account_code` stable for the same (login, server) pair — it follows from the formula, so
  just recompute it the same way every time.
* If the credentials are used by several parallel workers, give each worker its own persistent
  `device_code`, or the server may treat them as one device being hijacked.

---

## 8. Token lifetime

There is **no refresh-token mechanism** in the app. The token is stored on the device and used until
the server rejects it; then the user logs in again. An integration job should:

1. Cache the token and reuse it across calls.
2. On `401` / `ROUTE: Unauthenticated`, re-run `log_in_device` and retry once.
3. Not re-authenticate before every request — repeated logins can trigger the `429` rate limit.

---

## 9. End-to-end example

```bash
SERVER="https://smartup.online"
LOGIN="zarif@greenwhite"
PASSWORD="secret"
PROJECT="trade"

# --- account_code = sha256("<login>#<server_url>") ---
ACCOUNT_CODE=$(printf '%s' "${LOGIN}#${SERVER}" | shasum -a 256 | cut -d' ' -f1)

# --- password_hash = sha1(password) ---
PASSWORD_HASH=$(printf '%s' "$PASSWORD" | shasum -a 1 | cut -d' ' -f1)

# --- 1. log in --------------------------------------------------------------
TOKEN=$(curl -s -X POST "$SERVER/b/biruni/s:log_in_device" \
  -H "Content-Type: application/json" \
  -H "project_code: $PROJECT" \
  -d "{
        \"login\":\"$LOGIN\",
        \"password_hash\":\"$PASSWORD_HASH\",
        \"account_code\":\"$ACCOUNT_CODE\",
        \"device_name\":\"integration-worker-01\",
        \"device_code\":\"9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d\",
        \"device_version\":\"13\",
        \"device_sdk\":\"33\",
        \"version_code\":\"1\",
        \"version_name\":\"1.0.0\",
        \"device_kind\":\"A\"
      }" | jq -r '.token')

# --- 2. session info → filials ----------------------------------------------
curl -s -X GET "$SERVER/b/biruni/m:session_info_mobile" \
  -H "token: $TOKEN" \
  -H "lang_code: ru" | jq '.[4]'
# → [["trade","Smartup Trade",[["1","Head office"]]], ...]

FILIAL_ID=1

# --- 3. push a visit --------------------------------------------------------
curl -s -X POST "$SERVER/b/biruni/mt/sync:sync" \
  -H "Content-Type: text/plain" \
  -H "token: $TOKEN" \
  -H "project_code: $PROJECT" \
  -H "filial_id: $FILIAL_ID" \
  -H "timezone_code: Asia/Tashkent" \
  --data-binary @visit_entry.json
```

`visit_entry.json` is the envelope described in
[`tvt_save_person_visit.md`](./tvt_save_person_visit.md) section 1.2.

---

## 10. Checklist for an integration job

1. Fix `server_url` (`https://smartup.online` in production) and `project_code = "trade"`.
2. Generate one persistent `device_code` (UUID) per worker and store it.
3. Compute `account_code = sha256(login + "#" + server_url)` and
   `password_hash = sha1(password)`, both lowercase hex.
4. `POST b/biruni/s:log_in_device` → read `token`.
5. `GET b/biruni/m:session_info_mobile` with the `token` header → read index `4` (`projects`),
   find `project_code == "trade"`, pick a `filial_id`.
6. Cache the token. Send `token` + `project_code` + `filial_id` headers on every business call.
7. On `401` or `ROUTE: Unauthenticated`, re-login once and retry. On `429`, sleep for `Retry-After`
   seconds — never retry immediately.
