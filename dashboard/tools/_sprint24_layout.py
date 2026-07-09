from pathlib import Path

ROOT = Path(r"E:/GitHub/x-reminder/dashboard")

# sidebar.tsx - full targeted replacements
sb = ROOT / "components/layout/sidebar.tsx"
t = sb.read_text(encoding="utf-8")
t = t.replace(
    "  footer?: React.ReactNode;\n  className?: string;\n}",
    "  footer?: React.ReactNode;\n  className?: string;\n  onNavigate?: () => void;\n}",
)
t = t.replace("  className,\n}: SidebarProps)", "  className,\n  onNavigate,\n}: SidebarProps)")
old_cls = '''        "glass-panel relative z-sidebar flex h-full min-h-[32rem] flex-col overflow-x-hidden overflow-y-auto rounded-[1.75rem] p-4 shadow-lg",'''
new_cls = '''        "glass-panel relative z-sidebar flex h-full min-h-0 max-h-[min(85dvh,100%)] flex-col overflow-x-hidden overflow-y-auto rounded-[1.75rem] p-4 shadow-lg lg:min-h-[32rem] lg:max-h-none",'''
t = t.replace(old_cls, new_cls)
t = t.replace(
    '''        <Button
          variant="ghost"
          size="icon"
          type="button"
          onClick={onToggleCollapse}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="border border-white/8 bg-white/5 transition-all duration-300 hover:bg-white/10"
        >
          <m.span
            animate={{ rotate: collapsed ? 180 : 0 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
            className="inline-flex"
          >
            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </m.span>
        </Button>''',
    '''        {onToggleCollapse ? (
          <Button
            variant="ghost"
            size="icon"
            type="button"
            onClick={onToggleCollapse}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="shrink-0 border border-white/8 bg-white/5 transition-all duration-300 hover:bg-white/10 max-sm:min-h-11 max-sm:min-w-11"
          >
            <m.span
              animate={{ rotate: collapsed ? 180 : 0 }}
              transition={{ duration: 0.28, ease: "easeOut" }}
              className="inline-flex"
            >
              {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
            </m.span>
          </Button>
        ) : null}''',
)
t = t.replace('<nav className="flex-1 space-y-2">', '<nav className="flex-1 space-y-2" aria-label="Main navigation">')
t = t.replace(
    '"group relative flex items-center justify-between overflow-hidden rounded-xl px-3 py-2.5 text-sm transition-all duration-300",',
    '"group relative flex min-h-11 items-center justify-between overflow-hidden rounded-xl px-3 py-2.5 text-sm transition-all duration-300 touch-manipulation",',
)
t = t.replace(
    '''            <Link
              href={item.href}
              className={cn(''',
    '''            <Link
              href={item.href}
              onClick={() => onNavigate?.()}
              className={cn(''',
)
sb.write_text(t, encoding="utf-8")

# dashboard-app-shell
shell = ROOT / "components/layout/dashboard-app-shell.tsx"
st = shell.read_text(encoding="utf-8")
st = st.replace(
    'className="relative isolate min-h-screen overflow-x-hidden"',
    'className="relative isolate min-h-screen min-h-[100dvh] overflow-x-hidden"',
)
st = st.replace(
    'className="relative z-page-content mx-auto max-w-[1280px] space-y-4 p-4 md:p-5 lg:p-6"',
    'className="relative z-page-content mx-auto max-w-[1280px] space-y-4 safe-area-shell md:py-5 lg:py-6"',
)
st = st.replace(
    '<main id="main-content" className="pb-8" aria-label="Page content">',
    '<main id="main-content" className="pb-8 outline-none" aria-label="Page content" tabIndex={-1}>',
)
st = st.replace(
    '''          className={cn(
            "max-w-[90vw] overflow-hidden border-white/10 p-2",
            "bg-glass/20 shadow-glow backdrop-blur-2xl"
          )}''',
    '''          className={cn(
            "max-h-[min(92dvh,calc(100dvh-var(--safe-area-top)-var(--safe-area-bottom)-0.5rem))] w-[min(20rem,calc(100vw-var(--safe-area-left)-var(--safe-area-right)-1rem))] max-w-[90vw] overflow-hidden overflow-y-auto border-white/10 p-2",
            "bg-glass/20 shadow-glow backdrop-blur-2xl"
          )}''',
)
st = st.replace(
    '<Sidebar items={sidebarItems} collapsed={false} />',
    '<Sidebar items={sidebarItems} collapsed={false} onNavigate={() => setMobileOpen(false)} className="min-h-0 max-h-none" />',
)
shell.write_text(st, encoding="utf-8")

# navbar
nav = ROOT / "components/layout/navbar.tsx"
nt = nav.read_text(encoding="utf-8")
nt = nt.replace(
    'className="glass-panel relative z-sticky-header flex flex-col gap-4 rounded-[1.75rem] p-4 shadow-lg lg:flex-row lg:items-center lg:justify-between"',
    'className="glass-panel relative z-sticky-header flex flex-col gap-4 rounded-[1.75rem] p-4 shadow-lg lg:flex-row lg:items-center lg:justify-between"',
)
nt = nt.replace(
    '<div className="flex items-center gap-3">',
    '<div className="flex min-w-0 items-center gap-3">',
)
nt = nt.replace(
    '''        <Button variant="ghost" size="icon" type="button" className="lg:hidden" onClick={onMenuClick}>
          <Menu className="h-4 w-4" />
        </Button>''',
    '''        <Button
          variant="ghost"
          size="icon"
          type="button"
          className="shrink-0 lg:hidden max-sm:min-h-11 max-sm:min-w-11"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
          aria-expanded={false}
        >
          <Menu className="h-4 w-4" />
        </Button>''',
)
nt = nt.replace('<div>', '<div className="min-w-0 flex-1">')
nt = nt.replace(
    '<p className="text-lg font-semibold text-foreground">{title}</p>',
    '<p className="truncate text-lg font-semibold text-foreground">{title}</p>',
)
nt = nt.replace(
    '<p className="text-sm text-muted-foreground">{subtitle}</p>',
    '<p className="line-clamp-2 text-sm text-muted-foreground sm:line-clamp-1">{subtitle}</p>',
)
nav.write_text(nt, encoding="utf-8")

# top-navigation
tn = ROOT / "components/layout/top-navigation.tsx"
tt = tn.read_text(encoding="utf-8")
tt = tt.replace('className={cn("overflow-x-auto", className)}', 'className={cn("scrollbar-thin-x -mx-1 overflow-x-auto overscroll-x-contain px-1", className)}')
tt = tt.replace(
    '"rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300",',
    '"inline-flex min-h-11 shrink-0 items-center rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300 touch-manipulation",',
)
tn.write_text(tt, encoding="utf-8")

print("layout components ok")
