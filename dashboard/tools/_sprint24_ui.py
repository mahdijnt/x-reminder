from pathlib import Path
ROOT = Path(r"E:/GitHub/x-reminder/dashboard")

# dialog.tsx
d = ROOT / "components/ui/dialog.tsx"
dt = d.read_text(encoding="utf-8")
old = '''        "fixed left-[50%] top-[50%] z-dialog grid w-full max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 border border-glass-border glass-surface p-6 shadow-glow",
        "data-[state=open]:animate-ds-in",'''
new = '''        "fixed left-[50%] top-[50%] z-dialog grid w-[min(100%,calc(100vw-var(--safe-area-left)-var(--safe-area-right)-1rem))] max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 overflow-y-auto border border-glass-border glass-surface p-6 shadow-glow",
        "max-h-[min(90dvh,calc(100dvh-var(--safe-area-top)-var(--safe-area-bottom)-2rem))]",
        "data-[state=open]:animate-ds-in",'''
if old in dt:
    dt = dt.replace(old, new)
    d.write_text(dt, encoding="utf-8")

# dropdown
dd = ROOT / "components/ui/dropdown-menu.tsx"
ddt = dd.read_text(encoding="utf-8")
ddt = ddt.replace(
    "const [position, setPosition] = React.useState({ top: 0, left: 0, minWidth: 192 });",
    "const [position, setPosition] = React.useState({ top: 0, left: 0, minWidth: 192, maxHeight: 384 });",
)
old_up = '''    setPosition({
      top: rect.bottom + sideOffset,
      left: Math.max(8, Math.min(left, window.innerWidth - minWidth - 8)),
      minWidth,
    });'''
new_up = '''    const root = document.documentElement;
    const safeTop = parseFloat(getComputedStyle(root).getPropertyValue("--safe-area-top")) || 0;
    const safeBottom = parseFloat(getComputedStyle(root).getPropertyValue("--safe-area-bottom")) || 0;
    const safeLeft = parseFloat(getComputedStyle(root).getPropertyValue("--safe-area-left")) || 0;
    const safeRight = parseFloat(getComputedStyle(root).getPropertyValue("--safe-area-right")) || 0;
    const viewportPadding = 8;
    const maxHeight = Math.max(
      160,
      window.innerHeight - safeTop - safeBottom - viewportPadding * 2
    );
    let top = rect.bottom + sideOffset;
    const estimatedHeight = Math.min(maxHeight, 384);
    if (top + estimatedHeight > window.innerHeight - safeBottom - viewportPadding) {
      top = Math.max(safeTop + viewportPadding, rect.top - sideOffset - estimatedHeight);
    }

    setPosition({
      top,
      left: Math.max(safeLeft + viewportPadding, Math.min(left, window.innerWidth - minWidth - safeRight - viewportPadding)),
      minWidth,
      maxHeight,
    });'''
if old_up in ddt:
    ddt = ddt.replace(old_up, new_up)
ddt = ddt.replace(
    '"max-h-[min(24rem,calc(100vh-1rem))] overflow-y-auto overflow-x-hidden rounded-lg border border-glass-border bg-popover/95 p-1 text-popover-foreground shadow-glow backdrop-blur-xl animate-ds-in",',
    '"overflow-y-auto overflow-x-hidden rounded-lg border border-glass-border bg-popover/95 p-1 text-popover-foreground shadow-glow backdrop-blur-xl animate-ds-in",',
)
ddt = ddt.replace(
    "minWidth: position.minWidth,\n          zIndex:",
    "minWidth: position.minWidth,\n          maxHeight: position.maxHeight,\n          zIndex:",
)
ddt = ddt.replace(
    '"relative flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm outline-none transition-colors hover:bg-secondary/60 hover:text-foreground disabled:pointer-events-none disabled:opacity-50",',
    '"relative flex min-h-11 w-full items-center gap-2 rounded-md px-2 py-2 text-sm outline-none transition-colors hover:bg-secondary/60 hover:text-foreground focus-visible:bg-secondary/40 disabled:pointer-events-none disabled:opacity-50 touch-manipulation",',
)
dd.write_text(ddt, encoding="utf-8")

# table
tb = ROOT / "components/ui/table.tsx"
tbt = tb.read_text(encoding="utf-8")
tbt = tbt.replace(
    '<div className="relative w-full overflow-auto">',
    '<div className="relative w-full overflow-auto overscroll-x-contain scrollbar-thin-x">',
)
tbt = tbt.replace(
    '"w-full caption-bottom text-sm",',
    '"w-full min-w-[36rem] caption-bottom text-sm",',
)
tb.write_text(tbt, encoding="utf-8")

# section-card
sc = ROOT / "components/dashboard/section-card.tsx"
sct = sc.read_text(encoding="utf-8")
sct = sct.replace(
    '<CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">',
    '<CardHeader className="flex flex-col items-start justify-between gap-4 space-y-0 sm:flex-row">',
)
sct = sct.replace('{action}', '{action ? <div className="w-full shrink-0 sm:w-auto">{action}</div> : null}')
# wait that might duplicate - original was {action} inside header. Let me read file
sc.write_text(sct, encoding="utf-8")

# auth shell
auth = ROOT / "components/auth/auth-layout-shell.tsx"
at = auth.read_text(encoding="utf-8")
at = at.replace(
    'className={cn("relative isolate min-h-screen overflow-x-hidden", className)}',
    'className={cn("relative isolate min-h-screen min-h-[100dvh] overflow-x-hidden", className)}',
)
at = at.replace(
    'className="relative z-page-content mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-4 py-10"',
    'className="relative z-page-content mx-auto flex min-h-screen min-h-[100dvh] w-full max-w-md flex-col justify-center safe-area-shell py-10"',
)
auth.write_text(at, encoding="utf-8")

# button icon touch
btn = ROOT / "components/ui/button.tsx"
bt = btn.read_text(encoding="utf-8")
bt = bt.replace(
    '  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ring-offset-background",',
    '  "inline-flex touch-manipulation items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ring-offset-background",',
)
bt = bt.replace('icon: "h-10 w-10",', 'icon: "h-10 w-10 max-sm:min-h-11 max-sm:min-w-11",')
btn.write_text(bt, encoding="utf-8")

# input
inp = ROOT / "components/ui/input.tsx"
it = inp.read_text(encoding="utf-8")
it = it.replace('"flex h-10 w-full', '"flex h-11 w-full min-h-11 sm:h-10 sm:min-h-10')
inp.write_text(it, encoding="utf-8")

# notifications dropdown width
nm = ROOT / "components/navigation/notifications-menu.tsx"
nmt = nm.read_text(encoding="utf-8")
nmt = nmt.replace(
    '<DropdownMenuContent className="w-[22rem]">',
    '<DropdownMenuContent className="w-[min(22rem,calc(100vw-var(--safe-area-left)-var(--safe-area-right)-1.5rem))]">',
)
nmt = nmt.replace(
    'className="text-xs font-medium text-primary transition-colors hover:text-primary/80"',
    'className="min-h-11 rounded-md px-2 text-xs font-medium text-primary transition-colors hover:text-primary/80 touch-manipulation"',
)
nm.write_text(nmt, encoding="utf-8")

# user menu trigger touch target
um = ROOT / "components/navigation/user-menu.tsx"
umt = um.read_text(encoding="utf-8")
umt = umt.replace(
    '<DropdownMenuTrigger className="rounded-full">',
    '<DropdownMenuTrigger className="inline-flex rounded-full p-0.5 touch-manipulation max-sm:min-h-11 max-sm:min-w-11 max-sm:items-center max-sm:justify-center">',
)
um.write_text(umt, encoding="utf-8")

# page-section action
ps = ROOT / "app/_components/page-section.tsx"
pst = ps.read_text(encoding="utf-8")
pst = pst.replace('{action ? <div className="shrink-0">{action}</div> : null}', '{action ? <div className="w-full shrink-0 sm:w-auto">{action}</div> : null}')
ps.write_text(pst, encoding="utf-8")

# data-table overflow hint
dtbl = ROOT / "components/data-display/data-table.tsx"
dtblt = dtbl.read_text(encoding="utf-8")
dtblt = dtblt.replace(
    '<div className={cn("rounded-2xl border border-glass-border glass-surface p-2", className)}>',
    '<div className={cn("rounded-2xl border border-glass-border glass-surface p-2 overflow-hidden", className)}>',
)
dtbl.write_text(dtblt, encoding="utf-8")

# shell + navbar mobileNavOpen
shell = ROOT / "components/layout/dashboard-app-shell.tsx"
st = shell.read_text(encoding="utf-8")
if "mobileNavOpen" not in st:
    st = st.replace(
        "onMenuClick={() => setMobileOpen(true)}",
        "onMenuClick={() => setMobileOpen(true)}\n              mobileNavOpen={mobileOpen}",
    )
    shell.write_text(st, encoding="utf-8")

nav = ROOT / "components/layout/navbar.tsx"
nt = nav.read_text(encoding="utf-8")
if "mobileNavOpen" not in nt:
    nt = nt.replace("onMarkAllNotificationsRead?: () => void;", "onMarkAllNotificationsRead?: () => void;\n  mobileNavOpen?: boolean;")
    nt = nt.replace("onMarkAllNotificationsRead,\n}: NavbarProps)", "onMarkAllNotificationsRead,\n  mobileNavOpen = false,\n}: NavbarProps)")
    nt = nt.replace('aria-expanded={false}', "aria-expanded={mobileNavOpen}")
    nt = nt.replace(
        '<m.header',
        '<m.header\n      role="banner"',
    )
    nav.write_text(nt, encoding="utf-8")

print("ui patches ok")
