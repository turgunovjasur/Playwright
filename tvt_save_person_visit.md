# `tvt_save_person_visit` — Visit Entry Specification

Reference for the Integration department. This document describes **exactly what the Smartup SFA
(trade) mobile app sends to the server when a salesperson's visit is closed**, so that an external
job/service can produce the same payload and push visits through the same server method.

Everything below is derived from the app source, not from a server contract:

| What | Where in the app |
|---|---|
| Payload builder (root) | `xtrade/lib/kernel/trade/tvt/tvt_sync.dart` → `TvtSync.loadVisitEntry()` |
| Merchandising blocks | `xtrade/lib/kernel/trade/tvt/tvt_sync.dart` |
| Photo / video / audio / quiz / comment / note blocks | `smartup5x_core/lib/kernel/core/mvt/mvt_sync.dart` |
| Orders / stocks / equipment blocks | `smartup5x_anor/lib/kernel/anor/mvtm/mvtm_sync.dart` |
| Order (deal) body | `smartup5x_anor/lib/kernel/anor/mdeal/mdeal_sync.dart` → `MDealSync.getMDeal()` |
| Entry envelope | `smartup5x_core/lib/kernel/entry.dart` |
| Transport | `smartup5x_core/lib/kernel/sync_protocol.dart`, `.../android/.../SyncWorker.kt`, `SyncApi.kt` |

---

## 1. Transport

### 1.1 Endpoint

```
POST {server_url}/b/biruni/mt/sync:sync
Content-Type: text/plain
```

Headers:

| Header | Required | Description |
|---|---|---|
| `token` | yes | Session token of the authenticated user. |
| `project_code` | yes | Tenant project code. For this app it is `trade`. |
| `filial_id` | yes | Branch (filial) id the data belongs to. |
| `timezone_code` | no | IANA timezone id of the device, e.g. `Asia/Tashkent`. |

There is a secondary route used only for entries that were cached after a failed sync:

```
POST {server_url}/b/core/mt/sync:send_cached_entries
body: { "entries": "<json string of the same entry array>" }
```

The primary `sync:sync` route is the one an integration job should target.

### 1.2 Request body

The body is a **plain-text JSON object** (not form-encoded):

```json
{
  "laststamp": "<last sync stamp, empty string on first sync>",
  "entries": [ /* array of Entry objects, see 1.3 */ ],
  "device_info": "<optional, only sent on the first sync of a device>",
  "not_execute_tape_codes": [ /* optional, list of tape codes to skip */ ],
  "execute_tape": "N"
}
```

Notes:

* `entries` may contain **any mix of entry codes** — one sync call carries visits, collector
  requests, GPS tracks, etc. A job that only pushes visits sends an array of
  `tvt_save_person_visit` entries only.
* `execute_tape: "N"` tells the server to process the entries but **not** return reference-data
  ("tape") lines. This is the useful mode for an integration job: it makes the call write-only and
  keeps the response small.
* `laststamp` may be an empty string for a pure write-only push.

The app itself sends in one of two modes:

* **Batch** — the whole `entries` array in a single call (`syncWithOldMethod`).
* **One entry per call** — every entry except the last is sent alone with `execute_tape: "N"`, and
  the last call is made normally to also pull reference data down. This is the default on Android
  (`SyncWorker.kt`).

Either mode is accepted by the server. For an integration job, one entry per call with
`execute_tape: "N"` gives the cleanest per-visit success/error correlation.

### 1.3 Entry envelope

Every element of `entries` has this shape (`Entry.toJson()`):

```json
{
  "entry_id": 1740380400123,
  "filial_id": 1,
  "entry_code": "tvt_save_person_visit",
  "value": { /* the visit payload — sections 3..12 */ },
  "server_result": ""
}
```

| Field | Type | Description |
|---|---|---|
| `entry_id` | int | **Unique id of this entry.** For a visit it equals the visit id. The app generates it as `DateTime.now().millisecondsSinceEpoch` (see `MvtNext.visitId()`), so it is a 13-digit epoch-milliseconds value. It is the correlation key used in the response. Must be unique per entry. |
| `filial_id` | int | Same branch id as the `filial_id` header. |
| `entry_code` | string | Constant `"tvt_save_person_visit"` (`TvtPref.ENTRY_SAVE_PERSON_VISIT`). |
| `value` | object | The visit payload. Duplicated `filial_id` inside — see section 3. |
| `server_result` | string | Always `""` on send. Reserved for the server's answer. |

### 1.4 Response

The response is **plain text, line-oriented**. Each line is one record; the first character is the
record type and fields are separated by a **TAB** (`\t`):

| Prefix | Meaning | Format |
|---|---|---|
| `S` | Entry accepted | `S<entry_id>\t<optional payload>` |
| `E` | Entry rejected | `E<entry_id>\t<error message>` |
| `TA#` | Available-ids block (reference data) | `TA#<tape>\t<ids>` |
| anything else | Tape (reference data) line | `<tape>\t<values>` |

An integration job only needs the `S` / `E` lines. Correlate them back by `entry_id`.

Application behaviour on each outcome (`xtrade/lib/kernel/trade/database.dart`):

* `S<entry_id>` → the local visit is deleted (`TvtCore.removeTvtVisit`).
* `E<entry_id>\t<message>` → the error text is stored on the visit, photos/videos are put back into
  "saved" state, and the visit stays on the device for retry. A specific error class also triggers a
  "postponed deal" flow.

### 1.5 Binary files are NOT in this payload

Photos, videos and audio are **not** embedded. The payload only carries their SHA:

* `photo_sha` / `video_sha` / `audio_sha` = **lowercase hex SHA-256 of the file bytes**.
* The bytes are uploaded separately via `POST {server_url}/b/biruni/m:upload_files` as
  `multipart/form-data` (image/jpeg or image/png).
* Upload happens **after** a successful sync in the app, but the server accepts the visit even
  before the files arrive.

An integration job that has no real media should send empty arrays for the media blocks rather than
inventing SHAs.

---

## 2. Conventions used throughout the payload

| Convention | Details |
|---|---|
| Booleans | Always the strings `"Y"` / `"N"`, never JSON `true`/`false`. |
| Date-time | `dd.MM.yyyy HH:mm:ss` — e.g. `"24.02.2026 09:15:03"`. |
| Date only | `dd.MM.yyyy` — e.g. `"24.02.2026"`. |
| Coordinates | Single string `"<latitude>,<longitude>"`, e.g. `"41.311081,69.240562"`. Empty string when no fix. |
| Durations | Integer **seconds**. |
| Money / quantities | Frequently sent as **strings** (e.g. `"price": "12500.0"`, `"quantity": "3.0"`) to avoid float formatting drift. The tables below mark which. |
| `null` | Sent explicitly for optional ids that are not set. A few keys are omitted entirely instead — marked "conditional" below. |
| Ids | All `*_id` fields are server-side ids from reference data, **except** `entry_id` / `mobile_visit_id` which are device-generated. |

---

## 3. Root object — `value`

Built by `TvtSync.loadVisitEntry()`.

| Field | Type | Req. | Description |
|---|---|---|---|
| `filial_id` | int | yes | Branch id. Same as the envelope. |
| `room_id` | int | yes | Sales room / division (`mrf_rooms.room_id`) the visit was performed under. |
| `robot_id` | int | yes | Robot — the route/automation profile assigned to the salesperson (`mrf_robots.robot_id`). Determines allowed product sets, price types and whether tracking is on. |
| `person_id` | int | yes | **Client** id (`md_persons.person_id`) — the outlet that was visited. |
| `begun_on` | datetime | yes | When the visit was opened on the device. |
| `ended_on` | datetime | yes | When the visit was closed. Empty string if never closed. |
| `spent_time` | int | yes | Visit duration in **seconds**, measured on the device. |
| `start_location` | string | no | `"lat,lng"` captured when the visit was opened. May be `""`. |
| `end_location` | string | no | `"lat,lng"` captured when the visit was closed. May be `null`/`""`. |
| `person_closed` | `"Y"`/`"N"` | yes | `"Y"` when the salesperson marked the outlet as **closed / not working** at the time of the visit. Derived from `tvt_visit_headers.person_status` (`C` = closed, `N` = normal). |
| `has_postponed_order` | `"Y"`/`"N"` | yes | `"Y"` when a postponed (deferred) order exists for this visit. Defaults to `"N"`. |
| `mobile_visit_id` | int | yes | Device-side visit id. **Equals `entry_id`.** The server uses it for idempotency / dedup. |
| `deal_recom_calculation_method` | string | yes | Value of the branch setting `SYNC_SETTINGS_RECOMMENDED_PRODUCT_KIND`. `"I"` = recommendation by product, `"GT"` = by product group/type, `""` = not configured. It tells the server how to interpret the `stocks` block (see section 6). |
| `visit_note` | string | yes | Free-text note for the whole visit. `""` when none. |
| `photos` | array | yes | Section 4. |
| `videos` | array | yes | Section 4. |
| `audios` | array | yes | Section 4. |
| `quizs` | array | yes | Section 5. |
| `comments` | array | yes | Section 5. |
| `orders` | array | yes | Section 7. |
| `stocks` | array | yes | Section 6. |
| `equipments` | array | yes | Section 8. |
| `equipment_requests` | array | yes | Section 8. |
| `equipment_movements` | array | yes | Section 8. |
| `repair_requests` | array | yes | Section 8. |
| `equipment_binds` | array | yes | Section 8. |
| `presentations` | array | yes | Section 9. |
| `merchandisings` | array | yes | Section 10. |

All array fields are **always present**; they are `[]` when the corresponding module was not used.

---

## 4. Media blocks — `photos`, `videos`, `audios`

### `photos[]`

| Field | Type | Description |
|---|---|---|
| `photo_type_id` | int | Photo type from reference data (`mvt_photo_types`) — e.g. "shop front", "shelf". |
| `photo_sha` | string | SHA-256 of the image file, lowercase hex. |
| `photo_date` | datetime | When the photo was taken. |
| `latlng` | string | `"lat,lng"` at capture time. May be `null`. |
| `note` | string | Optional caption. May be `null`. |

### `videos[]`

| Field | Type | Description |
|---|---|---|
| `video_type_id` | int | Video type (`mvt_video_types`). |
| `video_sha` | string | SHA-256 of the video file. |
| `video_date` | datetime | Capture time. |
| `latlng` | string | `"lat,lng"`. May be `null`. |
| `note` | string | Optional. May be `null`. |

### `audios[]`

| Field | Type | Description |
|---|---|---|
| `audio_sha` | string | SHA-256 of the audio file. |
| `audio_date` | datetime | Recording time. |

---

## 5. `comments` and `quizs`

### `comments[]`

Predefined comment tags picked by the salesperson (not free text — free text lives in `visit_note`).

| Field | Type | Description |
|---|---|---|
| `comment_id` | int | Reference id from `mvt_comments`. |

### `quizs[]` — questionnaire results

Three nested levels. **Empty quiz sets are skipped** — a top-level element is only emitted when it
actually contains answered sets.

```
quizs[]
 ├─ quiz_set_id
 └─ quiz_sets[]
     ├─ quiz_set_id, result_quiz_set_id, parent_option_id, answer_id
     └─ quizs[]
         ├─ quiz_id, parent_option_id, answer_id, note
         ├─ answers[]  → option_id, answer, answer_id
         └─ photo_shas[]
```

**`quizs[]` (level 1)**

| Field | Type | Description |
|---|---|---|
| `quiz_set_id` | int | Root questionnaire id assigned to this visit. |
| `quiz_sets` | array | Level 2, below. |

**`quiz_sets[]` (level 2)**

| Field | Type | Description |
|---|---|---|
| `quiz_set_id` | int | Questionnaire (sub-set) id. |
| `result_quiz_set_id` | int | Device-side id of this filled-in set instance. Used to link nested sets. |
| `parent_option_id` | int \| null | Option that caused this set to appear (conditional/branching questionnaires). `null` for the root set. |
| `answer_id` | int \| null | Parent answer this set hangs off. `null` for the root set. |
| `quizs` | array | Level 3, below. |

**`quizs[]` (level 3 — the individual questions)**

| Field | Type | Description |
|---|---|---|
| `quiz_id` | int | Question id. |
| `parent_option_id` | int \| null | Option that revealed this question, for branching questions. |
| `answer_id` | int \| null | Parent answer id for nested questions. |
| `note` | string \| null | Free-text note attached to the answer. |
| `answers` | array | The chosen options / typed values, below. |
| `photo_shas` | array of string | SHA-256 of photos attached to this question. |

**`answers[]`**

| Field | Type | Description |
|---|---|---|
| `option_id` | int \| null | Chosen option id. `null` for free-input questions. |
| `answer` | string \| null | Typed/measured value for free-input questions. |
| `answer_id` | int | Device-side unique id of this answer row. Referenced by nested questions via their `answer_id`. |

---

## 6. `stocks` — remaining stock at the outlet

The **shape depends on `deal_recom_calculation_method`**:

### When `deal_recom_calculation_method == "GT"` (by product group/type)

| Field | Type | Description |
|---|---|---|
| `product_group_id` | int | Product group id. |
| `product_type_id` | int | Product type (sub-type) id. |
| `stock_quant` | string | Remaining quantity at the outlet, as a decimal string. May be `null`. |
| `intermediate_order_quant` | string | Quantity already ordered but not yet delivered. May be `null`. |

### Otherwise (by product — `"I"` or unset)

| Field | Type | Description |
|---|---|---|
| `inventory_kind` | string | `P` produce, `G` goods, `M` material, `E` equipment. |
| `product_id` | int | Product id. |
| `card_code` | string \| null | Batch/card code, when batch tracking is on. |
| `expiry_date` | string \| null | Batch expiry date (`dd.MM.yyyy`). |
| `stock_quant` | string | Remaining quantity, as a decimal string. |

---

## 7. `orders` — deals created during the visit

Each element is a full deal document produced by `MDealSync.getMDeal()`. One visit may produce
several: a sales order (`deal_kind = O`) and/or a return (`deal_kind = R`).

### 7.1 Deal header

| Field | Type | Description |
|---|---|---|
| `filial_id` | int | Branch. |
| `subfilial_id` | int \| null | Sub-branch, when the branch setting requires it. |
| `room_id` | int | Sales room. |
| `person_id` | int | Client id. |
| `currency_id` | int \| null | Currency of the deal. |
| `deal_time` | datetime | When the order was created on the device. |
| `delivery_date` | date | Requested delivery date. |
| `sales_manager_id` | int | The salesperson (`md_persons.person_id`). |
| `robot_id` | int | Robot/route the order was created under. |
| `expeditor_id` | int \| null | Assigned expeditor/driver. |
| `van_id` | int \| null | Assigned vehicle. |
| `payment_type_id` | int \| null | Payment type (`mkr_payment_types`). |
| `agreement_cashing_date` | date \| null | Agreed cashing date for deferred payment. |
| `checkbook_amount` | number \| null | Cheque book amount. |
| `check_number` | string \| null | Cheque number. |
| `contract_id` | int \| null | Contract the order is booked against. |
| `status` | string | Base status: `D` draft, `N` new, `B` booked, `A` archived, `C` cancelled, `B#S` shipped, `B#V` delivered. Orders sent from a visit are normally `N` or `B`. |
| `invoice_number` | string \| null | Invoice number, when the device issued one. |
| `source_table` | string | Always `MVTM_VISIT_HEADERS` for a deal created inside a visit. |
| `source_id` | int | The `mobile_visit_id` of the parent visit. |
| `note` | string \| null | Header note. |
| `deal_note` | string | Long note text for the deal (`""` when none). |
| `return_reason_id` | int \| null | Reason id — only for returns. |
| `delivery_address_short` | string \| null | Short delivery address. |
| `delivery_address_full` | string \| null | Full delivery address. |
| `delivery_latlng` | string \| null | `"lat,lng"` of the delivery point. |
| `request_id` | int \| null | Source order-request id, when the order came from a request. |
| `exchange_warehouse_id` | int \| null | Warehouse for exchange items. |
| `with_promotion` | `"Y"`/`"N"` | Whether promotion rules were applied. |
| `self_shipment` | `"Y"`/`"N"` | Client picks the goods up themselves. |
| `consignment_responsible_id` | int \| null | Person responsible for the consignment schedule. |
| `booked_payment_amount` | string | **Conditional** — present only when > 0. Prepaid/booked amount, as a decimal string. |
| `order_deal_id` | int \| null | **Returns only.** The original order this return refers to. |
| `warehouse_id` | int \| null | **Returns only.** Warehouse the goods are returned to. |
| `items` | array | Line items — 7.2 for orders, 7.3 for returns. |
| `consignments` | array | Payment schedule — 7.4. |

### 7.2 `items[]` for an order (`deal_kind = O`)

This array is a **union of five different line kinds**, distinguished by `price_type_id`:

| Line kind | Marker | Source |
|---|---|---|
| Normal product | real `price_type_id` | `mdeal_products` |
| Overload product | real `price_type_id` + `load_id` present | `mdeal_overload_products` |
| Promo gift | `price_type_id = "-1"` | `mdeal_promo_products` |
| Action/bonus product | `price_type_id = "-2"` | `mdeal_action_products` |
| Service | real `price_type_id`, no warehouse | `mdeal_service_products` |

**Normal product line**

| Field | Type | Description |
|---|---|---|
| `inventory_kind` | string | `P`/`G`/`M`/`E`. |
| `price_type_id` | int | Price type used. |
| `warehouse_id` | int \| null | Source warehouse. |
| `product_id` | int | Product id. |
| `card_id` | int \| null | Batch/card id. |
| `vat_percent` | number | VAT rate. |
| `price` | string | Unit price as a decimal string. |
| `quantity` | string | Ordered quantity as a decimal string. |
| `margin_value` | number \| null | Discount/markup value applied to the line. |
| `bonus_id` | int \| null | Legacy single-bonus field. Filled **only** when the line has exactly one margin whose `bonus_id > 0`; otherwise `null`. Kept for backward compatibility with older servers — prefer `product_margins`. |
| `product_margins` | array | Detailed discount breakdown: `{ bonus_id, calc_level, margin_value }`. `calc_level` is the order in which the discounts were stacked. `[]` when none. |
| `is_in_mml` | `"Y"`/`"N"` | Whether the product is in the client's Must-Have list (MML). |
| `recom_quant` | number \| null | Quantity the system recommended. |
| `recom_product_id` | int \| null | Product the recommendation was based on. |
| `product_kit_id` | array of int | Kit ids the line participates in. `[]` when none. |
| `is_exchange` | `"Y"`/`"N"` | Line is part of an exchange. |
| `marking_ids` | array of int | Ids of scanned marking (DataMatrix) codes. `[]` when none. |

**Overload product line** — same keys as a normal line, plus `load_id` (int, the overload rule
load), and without the margin/MML/recommendation fields.

**Promo gift line**

| Field | Type | Description |
|---|---|---|
| `product_unit_id` | int | **Conditional** — present only when the gift is bound to a specific order line. |
| `inventory_kind` | string | `P`/`G`/`M`/`E`. |
| `price_type_id` | `"-1"` | Constant marker for a promo gift. |
| `warehouse_id` | int | Source warehouse. |
| `product_id` | int | Gift product. |
| `margin_value` | `"0"` | Always zero. |
| `vat_percent` | `"0"` | Always zero. |
| `price` | `"0"` | Always zero. |
| `quantity` | string | Gift quantity as a decimal string. |
| `promotion_codes` | array of string | Scanned promo codes. `[]` when none. |

**Action product line** — `price_type_id = "-2"`, `price`/`vat_percent`/`margin_value` all `"0"`,
plus `bonus_id` (int) identifying the action bonus, `warehouse_id`, `product_id`, `inventory_kind`,
`quantity`.

**Service line**

| Field | Type | Description |
|---|---|---|
| `price_type_id` | int | Price type. |
| `product_id` | int | Service product id. |
| `margin_value` | number \| null | Discount value. |
| `vat_percent` | number \| null | VAT rate. |
| `price` | number | Service price. |
| `bonus_id` | int \| null | Bonus id. |
| `quantity` | string | Quantity as a decimal string. |

### 7.3 `items[]` for a return (`deal_kind = R`)

Lines with zero quantity are dropped.

| Field | Type | Description |
|---|---|---|
| `inventory_kind` | string | `P`/`G`/`M`/`E`. |
| `price_type` | int | **Note the different key name.** `-3` return price, `-2` action price, `-1` promo price. Derived from the price type pcode. |
| `warehouse_id` | int | Warehouse the goods go back to. |
| `product_id` | int | Product id. |
| `card_code` | string \| null | Batch/card code. |
| `expiry_date` | string \| null | Batch expiry date. |
| `vat_percent` | number | VAT rate. |
| `price` | string | Return price as a decimal string. |
| `input_price` | string | Original input price as a decimal string, `""` when unknown. |
| `quantity` | string | Returned quantity as a decimal string. |
| `margin_kind` | string | `A` amount, `P` percent, `""` when none. |
| `margin_value` | string | Discount value as a string, `""` when none. |
| `margin_amount` | string | Discount amount as a string, `""` when none. |
| `bonus_id` | int \| null | Bonus id. |
| `load_id` | int \| null | Overload load id. |
| `marking_ids` | array of int | **Conditional** — present only when marking codes were scanned. |

### 7.4 `consignments[]`

Payment schedule agreed at the point of sale. Rows without an amount are skipped.

| Field | Type | Description |
|---|---|---|
| `consignment_date` | date | Due date. |
| `consignment_amount` | string | Amount due as a decimal string. |

---

## 8. Equipment blocks

Five separate arrays, all built from the visit's equipment module.

### 8.1 `equipments[]` — equipment inventory check

| Field | Type | Description |
|---|---|---|
| `producer_code_id` | int \| null | Id of the registered producer/serial code of the unit. |
| `producer_code` | string \| null | The producer/serial code as text. |
| `scanned_barcode` | string \| null | Barcode scanned on site. At least one of `producer_code_id` / `scanned_barcode` is set. |
| `note` | string \| null | Note about the unit. |
| `photos` | array | `{ photo_sha, photo_date, latlng }` per photo. |
| `comments` | array | `{ comment_id }` — predefined comment tags. |

### 8.2 `equipment_requests[]` — requests for new equipment

Rows where no source person is set (i.e. a request to the company, not a transfer).

| Field | Type | Description |
|---|---|---|
| `visit_id` | int | Parent `mobile_visit_id`. |
| `request_kind` | string | Kind of request (install / removal / replacement — reference-defined). |
| `room_id` | int | Sales room. |
| `robot_id` | int | Robot/route. |
| `person_id` | int | Client the equipment is requested for. |
| `note` | string \| null | Free text. |
| `items` | array | Always exactly one element: `{ equipment_group_id, equipment_type_id, equipment_id, serial_id }`. Any of them may be `null` when the request is generic. |

### 8.3 `equipment_movements[]` — transfers between clients

Same shape as `equipment_requests[]`, but emitted for rows **that do** have a source person, and with
one extra key:

| Field | Type | Description |
|---|---|---|
| `from_person_id` | int | The client the unit is moved **from**. |
| `items` | array | One element: `{ equipment_id, serial_id }` (no group/type). |

### 8.4 `repair_requests[]` — repair requests

| Field | Type | Description |
|---|---|---|
| `room_id` | int | Sales room. |
| `person_id` | int | Client. |
| `robot_id` | int | Robot/route. |
| `visit_id` | int | Parent `mobile_visit_id`. |
| `note` | string \| null | Description of the problem. |
| `equipment_id` | int | Equipment product id. |
| `serial_id` | int | Serial id of the specific unit. |
| `breakage_ids` | array of int | Selected breakage/fault reference ids. |

### 8.5 `equipment_binds[]` — equipment characteristics

Which product sub-types are stocked in each unit. Grouped by (equipment, type).

| Field | Type | Description |
|---|---|---|
| `equipment_id` | int | Equipment product id. |
| `equipment_group_id` | int | Characteristic type id. |
| `equipment_type_ids` | array of int | The selected sub-type ids for that type. |
| `serial_id` | int | Serial id of the unit (from the visit's equipment row). |

---

## 9. `presentations[]`

Presentations shown to the client during the visit.

| Field | Type | Description |
|---|---|---|
| `presentation_id` | int | Presentation reference id. |
| `duration` | int | Full length of the presentation, in **seconds**. |
| `watching_time` | int | How long it was actually watched, in **seconds**. |

---

## 10. `merchandisings[]` — merchandising audit

One element per **merchandising setting** (`tmcgf_settings`) that produced at least one measured
product row during the visit. Settings with no measured rows are omitted entirely.

| Field | Type | Description |
|---|---|---|
| `setting_id` | int | Merchandising setting id. |
| `status_id` | int \| null | Outcome status chosen by the merchandiser. |
| `modules` | array | The evaluated modules. Only non-empty modules are included, in the order: assortment, planogram, shelf share, shelf price, POS material. |

Every module object shares three keys:

| Field | Type | Description |
|---|---|---|
| `module_kind` | string | `A` assortment, `P` planogram, `S` shelf share, `R` shelf price (price tag), `D` POS material / display. |
| `plan_score` | number | Maximum points achievable for this module in this visit. |
| `fact_score` | number | Points actually earned. |

Scores are computed on the device by summing the per-reference scores; both are rounded to 4
decimal places.

### 10.1 Assortment module (`module_kind = "A"`)

```
{ module_kind, plan_score, fact_score, assorments: [...] }
```

> Note the key spelling: **`assorments`** (single `t`). It is spelled this way in the app and must be
> matched exactly.

**`assorments[]`**

| Field | Type | Description |
|---|---|---|
| `assortment_id` | int | Assortment (product list) id. |
| `item_count` | int | Number of products in the assortment. |
| `plan_available_count` | int | How many were expected to be present. |
| `fact_available_count` | int | How many were actually present. |
| `plan_score` | number | Points achievable for this assortment. |
| `fact_score` | number | Points earned. |
| `assortment_items` | array | Per-product result, below. |
| `photos` | array of string | Photo SHAs taken for this assortment. |

**`assortment_items[]`**

| Field | Type | Description |
|---|---|---|
| `product_id` | int | Product id. |
| `has_product` | `"Y"`/`"N"` | Whether the product was found on the shelf. |
| `quantity` | int \| null | Stock quantity counted. |
| `refuse_reason_id` | int \| null | Reason id when `has_product = "N"`. |
| `automatic_detected_face_quant` | int \| null | Facings detected automatically by image recognition, when enabled. |

### 10.2 Planogram module (`module_kind = "P"`)

```
{ module_kind, plan_score, fact_score, planograms: [...] }
```

**`planograms[]`**

| Field | Type | Description |
|---|---|---|
| `sample_id` | int | Planogram sample (template) id. |
| `item_count` | int | Number of products in the sample. |
| `plan_correspond_count` | int | How many were expected to match the planogram. |
| `fact_correspond_count` | int | How many actually matched. |
| `plan_score` | number | Points achievable. |
| `fact_score` | number | Points earned. |
| `planogram_items` | array | Per-product result, below. |
| `photos` | array of string | Photo SHAs of the shelf. Legacy flat list. |
| `planogram_photos` | array | Newer form of the same photos, with recognition results — below. |
| `purity` | int | **Conditional** — included only when set and non-zero. Shelf cleanliness score. |
| `device_screen` | `"Y"`/`"N"` | **Conditional** — included only when the value exists. Whether the photo was taken of a device screen rather than a real shelf (anti-fraud signal). |

**`planogram_items[]`** — contains both in-planogram and out-of-planogram products.

| Field | Type | Description |
|---|---|---|
| `product_id` | int | Product id. |
| `sample_unit_id` | int \| null | Specific shelf position in the sample. `null` when not position-bound. |
| `correspond` | `"Y"`/`"N"` | Whether the product matched the planogram. Always `"N"` for out-of-planogram rows. |
| `row_number` | int \| null | Shelf row the product was found on. |
| `is_planogram` | `"Y"`/`"N"` | `"Y"` — product belongs to the planogram sample; `"N"` — extra product found on the shelf that is not in the sample. |
| `refuse_reason_id` | int \| null | Reason id when the product did not match. |
| `plan_face_quant` | int \| null | Facings required by the sample. `null` for out-of-planogram rows. |
| `fact_face_quant` | int \| null | Facings detected automatically from the photo. |
| `correspond_face_quant` | int | **Conditional** — included only when set and non-zero. Facings that actually matched. |

**`planogram_photos[]`**

Without image recognition:

```json
{ "photo_sha": "<sha256>" }
```

With image recognition results available:

```json
{
  "photo_sha": "<sha256>",
  "coordinates": [
    { "product_name": "Product A", "bboxes": [[x1, y1, x2, y2], ...] }
  ]
}
```

`bboxes` are pixel bounding boxes on the photo, each as `[x1, y1, x2, y2]`.

### 10.3 Shelf share module (`module_kind = "S"`)

```
{ module_kind, plan_score, fact_score, shelf_shares: [...] }
```

**`shelf_shares[]`**

| Field | Type | Description |
|---|---|---|
| `assortment_id` | int | Assortment id. |
| `plan_percent` | int | Target share of shelf, in percent (`plan_correspond_count / item_count * 100`, truncated). |
| `fact_percent` | int | Achieved share, same formula with the fact count. |
| `fact_face_count` | int | Number of products in the assortment used as the base of the calculation. |
| `plan_score` | number | Points achievable. |
| `fact_score` | number | Points earned. |
| `shelf_share_items` | array | `{ product_id, face_quantity }` — own facings counted per product (`0` when not counted). |
| `competitor_products` | array | Competitor facings, below. |

**`competitor_products[]`**

| Field | Type | Description |
|---|---|---|
| `competitor_id` | int | Competitor reference id. |
| `product_id` | int | Competitor product id. |
| `has_product` | `"Y"`/`"N"` | Whether the competitor product was present. |
| `face_quantity` | int \| null | Facings counted manually. |
| `price` | number \| null | Competitor shelf price. |
| `automatic_detected_face_quant` | int \| null | Facings detected automatically from the photo. |

### 10.4 Shelf price module (`module_kind = "R"`)

```
{ module_kind, plan_score, fact_score, shelf_prices: [...] }
```

**`shelf_prices[]`**

| Field | Type | Description |
|---|---|---|
| `assortment_id` | int | Assortment id. |
| `item_count` | int | Products in the assortment. |
| `plan_price_avail_count` | int | How many price tags were expected. |
| `fact_price_avail_count` | int | How many were actually present and correct. |
| `plan_score` | number | Points achievable. |
| `fact_score` | number | Points earned. |
| `shelf_price_items` | array | Per-product result, below. |

**`shelf_price_items[]`**

| Field | Type | Description |
|---|---|---|
| `product_id` | int | Product id. |
| `has_price` | `"Y"`/`"N"` | Whether a price tag was present. |
| `price` | number \| null | Price read from the tag. |
| `refuse_reason_id` | int \| null | Reason id when `has_price = "N"`. |

### 10.5 POS material / display module (`module_kind = "D"`)

```
{ module_kind, plan_score, fact_score, displays: [...] }
```

Scoring for this module is computed on the device from the setting's `score` and `separate_kind`:

* `separate_kind = "E"` (per product): `plan_score = score × display_count`,
  `fact_score = score × present_count`.
* otherwise: `plan_score = score`, `fact_score = score / display_count × present_count`.

**`displays[]`**

| Field | Type | Description |
|---|---|---|
| `display_id` | int | POS material / display reference id. |
| `has_display` | `"Y"`/`"N"` | Whether the material was in place. |
| `consumption_quantity` | int \| null | Quantity of material consumed/left at the outlet. |
| `refuse_reason_id` | int \| null | Reason id when `has_display = "N"`. |
| `photos` | array of string | Photo SHAs. Contains at most one element; `[]` when no photo. |

---

## 11. Full example

A short but structurally complete visit: a closed visit with one photo, one order line, a stock
count and one assortment module.

```json
{
  "laststamp": "",
  "execute_tape": "N",
  "entries": [
    {
      "entry_id": 1771920903123,
      "filial_id": 1,
      "entry_code": "tvt_save_person_visit",
      "server_result": "",
      "value": {
        "filial_id": 1,
        "room_id": 12,
        "robot_id": 305,
        "person_id": 884512,
        "begun_on": "24.02.2026 09:15:03",
        "ended_on": "24.02.2026 09:41:58",
        "spent_time": 1615,
        "start_location": "41.311081,69.240562",
        "end_location": "41.311090,69.240570",
        "person_closed": "N",
        "has_postponed_order": "N",
        "mobile_visit_id": 1771920903123,
        "deal_recom_calculation_method": "I",
        "visit_note": "Client asked for extra promo materials",

        "photos": [
          {
            "photo_type_id": 3,
            "photo_sha": "9f2c1b7d4a6e5c8f0b3d2a1e7c9f4b6d8a0c2e4f6b8d0a2c4e6f8b0d2a4c6e8f",
            "photo_date": "24.02.2026 09:20:11",
            "latlng": "41.311081,69.240562",
            "note": null
          }
        ],
        "videos": [],
        "audios": [],

        "quizs": [
          {
            "quiz_set_id": 41,
            "quiz_sets": [
              {
                "quiz_set_id": 41,
                "result_quiz_set_id": 1771920903124,
                "parent_option_id": null,
                "answer_id": null,
                "quizs": [
                  {
                    "quiz_id": 512,
                    "parent_option_id": null,
                    "answer_id": null,
                    "note": null,
                    "answers": [
                      { "option_id": 9001, "answer": null, "answer_id": 1771920903125 }
                    ],
                    "photo_shas": []
                  }
                ]
              }
            ]
          }
        ],
        "comments": [ { "comment_id": 7 } ],

        "stocks": [
          {
            "inventory_kind": "G",
            "product_id": 55021,
            "card_code": null,
            "expiry_date": null,
            "stock_quant": "12.0"
          }
        ],

        "orders": [
          {
            "filial_id": 1,
            "subfilial_id": null,
            "room_id": 12,
            "person_id": 884512,
            "currency_id": 1,
            "deal_time": "24.02.2026 09:33:40",
            "delivery_date": "25.02.2026",
            "sales_manager_id": 771003,
            "robot_id": 305,
            "expeditor_id": null,
            "payment_type_id": 2,
            "agreement_cashing_date": null,
            "checkbook_amount": null,
            "check_number": null,
            "van_id": null,
            "contract_id": 45011,
            "status": "N",
            "invoice_number": null,
            "source_table": "MVTM_VISIT_HEADERS",
            "source_id": 1771920903123,
            "note": null,
            "return_reason_id": null,
            "delivery_address_short": "Chilonzor 9",
            "delivery_address_full": "Tashkent, Chilonzor 9, shop 4",
            "delivery_latlng": "41.311081,69.240562",
            "request_id": null,
            "exchange_warehouse_id": null,
            "with_promotion": "Y",
            "self_shipment": "N",
            "consignment_responsible_id": null,
            "items": [
              {
                "inventory_kind": "G",
                "price_type_id": 4,
                "warehouse_id": 61,
                "product_id": 55021,
                "card_id": null,
                "vat_percent": 12,
                "price": "12500.0",
                "quantity": "24.0",
                "margin_value": 5,
                "bonus_id": 3301,
                "product_margins": [
                  { "bonus_id": 3301, "calc_level": 1, "margin_value": 5 }
                ],
                "is_in_mml": "Y",
                "recom_quant": 20,
                "product_kit_id": [],
                "recom_product_id": null,
                "is_exchange": "N",
                "marking_ids": []
              }
            ],
            "consignments": [
              { "consignment_date": "10.03.2026", "consignment_amount": "300000.0" }
            ],
            "deal_note": ""
          }
        ],

        "equipments": [],
        "equipment_requests": [],
        "equipment_movements": [],
        "repair_requests": [],
        "equipment_binds": [],

        "presentations": [
          { "presentation_id": 88, "duration": 120, "watching_time": 95 }
        ],

        "merchandisings": [
          {
            "setting_id": 17,
            "status_id": 2,
            "modules": [
              {
                "module_kind": "A",
                "plan_score": 10.0,
                "fact_score": 7.5,
                "assorments": [
                  {
                    "assortment_id": 205,
                    "item_count": 4,
                    "plan_available_count": 4,
                    "fact_available_count": 3,
                    "plan_score": 10.0,
                    "fact_score": 7.5,
                    "assortment_items": [
                      {
                        "product_id": 55021,
                        "has_product": "Y",
                        "quantity": 12,
                        "refuse_reason_id": null,
                        "automatic_detected_face_quant": 5
                      },
                      {
                        "product_id": 55022,
                        "has_product": "N",
                        "quantity": null,
                        "refuse_reason_id": 902,
                        "automatic_detected_face_quant": null
                      }
                    ],
                    "photos": [
                      "1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f708192a3b4c5d6e7f809"
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    }
  ]
}
```

Example response:

```
S1771920903123
```

or, on failure:

```
E1771920903123	A02-16-105: Contract 45011 is expired
```

---

## 12. Related entry codes (for context)

The same sync call may also carry these, produced by the same app. They are **out of scope** for the
visit job but share the envelope and response format:

| Entry code | What it carries | Builder |
|---|---|---|
| `save_user_track` | GPS track point: `robot_id`, `track_time`, `track_kind`, `latlng`, `note` | `TvtSync.loadUserTracks()` |
| `save_dual_visit` | Dual (supervisor) visit with its quiz marks | `TvtSync.loadDualVisitEntry()` |
| `visit_postponed_order_save` | A deferred order created from a visit | `MvtmSync.loadVisitPostponedDeals()` |
| `anor_visit_save` | The **generic Anor visit** — a strict subset of `tvt_save_person_visit` without merchandising, presentations, `person_closed`, `spent_time` and `deal_recom_calculation_method` | `MvtmSync.loadVisitEntry()` |

---

## 13. Checklist for an integration job

1. Authenticate and obtain a `token` for the target `filial_id` / `project_code = trade`.
2. Generate a unique `entry_id` per visit — 13-digit epoch milliseconds is what the app uses, and it
   must equal `value.mobile_visit_id`. Any deal created inside the visit must repeat it in
   `source_id` with `source_table = "MVTM_VISIT_HEADERS"`.
3. Build `value` per sections 3–10. Send `[]` for unused module arrays — do not omit the keys.
4. Use `"Y"`/`"N"` strings for booleans and `dd.MM.yyyy HH:mm:ss` for date-times.
5. If media is involved, upload the file bytes to `b/biruni/m:upload_files` and put the lowercase
   hex SHA-256 in the corresponding `*_sha` field.
6. POST the envelope to `b/biruni/mt/sync:sync` with `"execute_tape": "N"` to keep the call
   write-only.
7. Parse the plain-text response line by line; treat `S<entry_id>` as accepted and
   `E<entry_id>\t<message>` as rejected, and retry rejected entries after fixing the cause.
