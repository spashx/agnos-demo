// RQ-DSN-003, RQ-DSN-005, DEC-DSN-002 (ADR-DSN-001)

/** RQ-DSN-005: the class names shared by the stylesheet and the views, so a selector and its markup cannot drift apart. */
export const CLASS = {
  page: "page",
  pageHeader: "page-header",
  title: "title",
  heading: "heading",
  caption: "caption",
  card: "card",
  table: "table",
  badge: "badge",
  badgeOpen: "badge-open",
  badgeClosed: "badge-closed",
  banner: "banner",
  bannerSuccess: "banner-success",
  bannerError: "banner-error",
  bannerWarning: "banner-warning",
  form: "form",
  field: "field",
  fieldLabel: "field-label",
  fieldControl: "field-control",
  actions: "actions",
  button: "button",
  buttonPrimary: "button-primary",
  buttonSecondary: "button-secondary",
  buttonDanger: "button-danger",
} as const;
