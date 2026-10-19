<!-- RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-005, RQ-WEB-006 (FTR-WEB-001); design system FTR-DSN-001, RQ-DSN-003, DEC-DSN-002 (ADR-DSN-001) -->
# Roombook web interface: screens and states

Written by the UX designer for FTR-WEB-001. Values are token names from `tokens.json`, never colours or sizes
(section 7.4 of FTR-DSN-001). The interface is one page with up to three cards in a single column.

## Page

```
+--------------------------------------------------+   page: page.background, page.text, page.maxWidth
|  Roombook                                        |   title: text.title.size, text.strong.weight
|  Meeting-room booking                            |   caption: text.caption.size, text.caption.color
|                                                  |
|  [ banner: shown after an action ]               |   banner: see states below
|                                                  |
|  +--------------------------------------------+  |   card: card.background, card.border, card.radius
|  | Rooms                                      |  |
|  | Room     Capacity   Status                 |  |   table: table.headerBackground, table.rowBorder
|  | Atlas    6          (check Open)            |  |   badge: badge.open.*, badge.closed.*
|  | Boreal   2          (cross Closed)          |  |
|  +--------------------------------------------+  |
|  +--------------------------------------------+  |
|  | Book a room                                |  |
|  | Room [ Atlas v ]                           |  |   field: field.*, one per row, label above
|  | Organizer [            ]                   |  |
|  | Start [            ] End [            ]    |  |
|  | Attendees [   ]                            |  |
|  | [ Book this room ]                         |  |   button.primary.*
|  +--------------------------------------------+  |
|  +--------------------------------------------+  |
|  | Cancel a reservation                       |  |
|  | Reservation identifier [            ]      |  |
|  | [ Cancel reservation ]                     |  |   button.secondary.*
|  +--------------------------------------------+  |
+--------------------------------------------------+
```

## Flows

| Trigger | Result | Banner |
|---|---|---|
| Open the page | Rooms listed, forms shown | none |
| Submit the booking form, accepted | Page reloads, form emptied | success: reservation identifier and a danger button "Cancel this reservation" |
| Submit the booking form, refused | Page reloads, typed values kept | error: wording of the code (conflict, capacity, closed room) |
| Submit the booking form, incomplete | Page reloads, typed values kept | error: every field is required |
| Submit the cancel form, accepted | Page reloads | success: the reservation is cancelled |
| Submit the cancel form, unknown identifier | Page reloads | error: no reservation has this identifier |
| Service does not answer | Title and banner only, no card | warning: the service does not answer |

## Banner states

| Kind | Tokens | Role announced | Cue other than colour |
|---|---|---|---|
| Success | `banner.success.background`, `banner.success.text` | status | the sentence names the reservation |
| Error | `banner.error.background`, `banner.error.text` | alert | the sentence states the cause |
| Warning | `banner.warning.background`, `banner.warning.text` | status | the sentence states what to do |

The warning text colour was darkened after the contrast test failed (TASK-DSN-003); see the `notes` entry of
`tokens.json`.

## Room statuses

| Status | Badge | Words and symbol | In the room list of the booking form |
|---|---|---|---|
| Open | `badge.open.*` | check mark and "Open" | selectable |
| Closed | `badge.closed.*` | cross and "Closed" | listed as "(closed)" and disabled |

## Wording rules

All visible texts are in `client/src/ui/labels.ts`. Buttons start with a verb that says what happens ("Book
this room", "Cancel reservation"), never with "Submit". Error banners say what to do next.

## Open points

- A list of the visitor's reservations would remove the need to copy an identifier; it needs a service route
  that does not exist yet.
- A dark theme only remaps semantic tokens (section 2.1 of FTR-DSN-001); it is out of scope for this release.
