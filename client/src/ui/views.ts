// RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-006, DEC-WEB-001 (ADR-WEB-001); RQ-DSN-005, DEC-DSN-002 (ADR-DSN-001)
import type { Room } from "../types.ts";
import { CLASS } from "./classes.ts";
import { LABEL } from "./labels.ts";
import { FORM_FIELD, ROUTE } from "./routes.ts";

const BANNER_CLASS = {
  success: CLASS.bannerSuccess,
  error: CLASS.bannerError,
  warning: CLASS.bannerWarning,
} as const;

const BANNER_ROLE = { success: "status", error: "alert", warning: "status" } as const;
const HTML_ESCAPES: Readonly<Record<string, string>> = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
const HTML_SPECIAL_PATTERN = /[&<>"']/g;
const MIN_ATTENDEES = "1";
const VIEWPORT_CONTENT = "width=device-width, initial-scale=1";
const DOCTYPE = "<!doctype html>";
const NO_VALUE = "";
const JOIN_NONE = "";

/** RQ-WEB-003: the kind of a banner decides its tokens, its ARIA role and its text cue. */
export type BannerKind = keyof typeof BANNER_CLASS;

/** RQ-WEB-002, RQ-WEB-003: a message shown above the cards; a success may carry the reservation it confirms. */
export interface Banner {
  readonly kind: BannerKind;
  readonly text: string;
  readonly reservationId?: string;
}

/** RQ-WEB-003: the values of the booking form, kept so a refused request does not lose what was typed. */
export interface FormValues {
  readonly roomId: string;
  readonly organizer: string;
  readonly start: string;
  readonly end: string;
  readonly attendees: string;
}

/** RQ-WEB-001: everything a page needs; the forms are left out when the service does not answer. */
export interface PageModel {
  readonly rooms: readonly Room[];
  readonly formsEnabled: boolean;
  readonly banner?: Banner;
  readonly values?: FormValues;
}

/** RQ-WEB-006: the values of an untouched booking form. */
export const EMPTY_VALUES: FormValues = { roomId: NO_VALUE, organizer: NO_VALUE, start: NO_VALUE, end: NO_VALUE, attendees: NO_VALUE };

/** RQ-WEB-006: escapes text for HTML content and attribute values, so service data cannot inject markup. */
export function escapeHtml(text: string): string {
  return text.replace(HTML_SPECIAL_PATTERN, (character) => HTML_ESCAPES[character]);
}

/** RQ-WEB-001: the rooms table, with a text-and-symbol status next to the badge colour. */
export function renderRoomsTable(rooms: readonly Room[]): string {
  if (rooms.length === 0) {
    return `<p class="${CLASS.caption}">${escapeHtml(LABEL.noRooms)}</p>`;
  }
  const head = [LABEL.columnName, LABEL.columnCapacity, LABEL.columnStatus].map((title) => `<th scope="col">${escapeHtml(title)}</th>`).join(JOIN_NONE);
  const rows = rooms.map((room) => `<tr><td>${escapeHtml(room.name)}</td><td>${room.capacity}</td><td>${renderBadge(room.open)}</td></tr>`).join(JOIN_NONE);
  return `<table class="${CLASS.table}"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table>`;
}

/** RQ-WEB-001: the open or closed badge. */
function renderBadge(open: boolean): string {
  const modifier = open ? CLASS.badgeOpen : CLASS.badgeClosed;
  return `<span class="${CLASS.badge} ${modifier}">${escapeHtml(open ? LABEL.statusOpen : LABEL.statusClosed)}</span>`;
}

/** RQ-WEB-002, RQ-WEB-006: a labelled form control; the label is bound to the control by `for` and `id`. */
function renderField(name: string, label: string, control: string): string {
  return `<div class="${CLASS.field}"><label class="${CLASS.fieldLabel}" for="${name}">${escapeHtml(label)}</label>${control}</div>`;
}

function renderInput(name: string, type: string, value: string, extra: string = NO_VALUE): string {
  return `<input class="${CLASS.fieldControl}" id="${name}" name="${name}" type="${type}" value="${escapeHtml(value)}" required ${extra}>`;
}

/** RQ-WEB-002: the room list of the booking form; a closed room is shown but cannot be chosen. */
function renderRoomSelect(rooms: readonly Room[], selected: string): string {
  const options = rooms.map((room) => {
    const label = room.open ? room.name : room.name + LABEL.closedSuffix;
    const state = (room.id === selected ? " selected" : NO_VALUE) + (room.open ? NO_VALUE : " disabled");
    return `<option value="${escapeHtml(room.id)}"${state}>${escapeHtml(label)}</option>`;
  });
  return `<select class="${CLASS.fieldControl}" id="${FORM_FIELD.roomId}" name="${FORM_FIELD.roomId}" required>${options.join(JOIN_NONE)}</select>`;
}

/** RQ-WEB-002, RQ-WEB-004: the actions row of a form, holding its submit button of the given variant. */
function renderActions(variant: string, label: string): string {
  const button = `<button class="${CLASS.button} ${variant}" type="submit">${escapeHtml(label)}</button>`;
  return `<div class="${CLASS.actions}">${button}</div>`;
}

/** RQ-WEB-002, RQ-WEB-004: a form posting URL-encoded values to a route. */
function renderPostForm(route: string, content: string, className: string = NO_VALUE): string {
  const classAttribute = className === NO_VALUE ? NO_VALUE : ` class="${className}"`;
  return `<form${classAttribute} method="post" action="${route}">${content}</form>`;
}

/** RQ-WEB-002: the booking form. */
export function renderBookingForm(rooms: readonly Room[], values: FormValues): string {
  const fields = [
    renderField(FORM_FIELD.roomId, LABEL.fieldRoom, renderRoomSelect(rooms, values.roomId)),
    renderField(FORM_FIELD.organizer, LABEL.fieldOrganizer, renderInput(FORM_FIELD.organizer, "text", values.organizer)),
    renderField(FORM_FIELD.start, LABEL.fieldStart, renderInput(FORM_FIELD.start, "datetime-local", values.start)),
    renderField(FORM_FIELD.end, LABEL.fieldEnd, renderInput(FORM_FIELD.end, "datetime-local", values.end)),
    renderField(FORM_FIELD.attendees, LABEL.fieldAttendees, renderInput(FORM_FIELD.attendees, "number", values.attendees, `min="${MIN_ATTENDEES}"`)),
  ];
  return renderPostForm(ROUTE.book, fields.join(JOIN_NONE) + renderActions(CLASS.buttonPrimary, LABEL.bookButton), CLASS.form);
}

/** RQ-WEB-004: the cancel form, asking for a reservation identifier. */
export function renderCancelForm(): string {
  const field = renderField(FORM_FIELD.reservationId, LABEL.fieldReservationId, renderInput(FORM_FIELD.reservationId, "text", NO_VALUE));
  return renderPostForm(ROUTE.cancel, field + renderActions(CLASS.buttonSecondary, LABEL.cancelButton), CLASS.form);
}

/** RQ-WEB-004: the one-click cancel form carried by the confirmation of a booking. */
function renderCancelThis(reservationId: string): string {
  const hidden = `<input type="hidden" name="${FORM_FIELD.reservationId}" value="${escapeHtml(reservationId)}">`;
  return renderPostForm(ROUTE.cancel, hidden + renderActions(CLASS.buttonDanger, LABEL.cancelThisButton));
}

/** RQ-WEB-003: a banner whose ARIA role tells assistive technology how urgent it is. */
export function renderBanner(banner: Banner): string {
  const cancel = banner.reservationId === undefined ? NO_VALUE : renderCancelThis(banner.reservationId);
  return `<div class="${CLASS.banner} ${BANNER_CLASS[banner.kind]}" role="${BANNER_ROLE[banner.kind]}"><p>${escapeHtml(banner.text)}</p>${cancel}</div>`;
}

function renderCard(heading: string, content: string): string {
  return `<section class="${CLASS.card}"><h2 class="${CLASS.heading}">${escapeHtml(heading)}</h2>${content}</section>`;
}

/** RQ-WEB-001, RQ-WEB-006: a whole page, linking the generated stylesheet. */
export function renderPage(model: PageModel): string {
  const banner = model.banner === undefined ? NO_VALUE : renderBanner(model.banner);
  const cards = model.formsEnabled
    ? [
        renderCard(LABEL.roomsHeading, renderRoomsTable(model.rooms)),
        renderCard(LABEL.bookHeading, renderBookingForm(model.rooms, model.values ?? EMPTY_VALUES)),
        renderCard(LABEL.cancelHeading, renderCancelForm()),
      ].join(JOIN_NONE)
    : NO_VALUE;
  const header = `<header class="${CLASS.pageHeader}"><h1 class="${CLASS.title}">${escapeHtml(LABEL.pageTitle)}</h1><p class="${CLASS.caption}">${escapeHtml(LABEL.pageSubtitle)}</p></header>`;
  const head = `<meta charset="utf-8"><meta name="viewport" content="${VIEWPORT_CONTENT}"><title>${escapeHtml(LABEL.pageTitle)}</title><link rel="stylesheet" href="${ROUTE.styles}">`;
  return `${DOCTYPE}<html lang="en"><head>${head}</head><body><main class="${CLASS.page}">${header}${banner}${cards}</main></body></html>`;
}

/** RQ-WEB-001: the page shown for an unknown route. */
export function renderNotFound(): string {
  return renderPage({ rooms: [], formsEnabled: false, banner: { kind: "warning", text: LABEL.notFoundText } });
}
