export const Z_INDEX = {
  background: 0,
  aurora: 1,
  pageContent: 10,
  card: 20,
  stickyHeader: 30,
  sidebar: 40,
  dropdown: 50,
  popover: 60,
  dialogOverlay: 70,
  dialog: 80,
  modal: 90,
  toast: 100,
} as const;

export type ZIndexLayer = keyof typeof Z_INDEX;
