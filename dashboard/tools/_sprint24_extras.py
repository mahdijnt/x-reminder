from pathlib import Path
ROOT = Path(r"E:/GitHub/x-reminder/dashboard")

shell = ROOT / "components/layout/dashboard-app-shell.tsx"
st = shell.read_text(encoding="utf-8")
st = st.replace(
    'className="relative z-page-content mx-auto max-w-[1280px] space-y-4 safe-area-shell md:py-5 lg:py-6"',
    'className="relative z-page-content mx-auto max-w-[1280px] space-y-4 px-[max(1rem,var(--safe-area-left))] pb-[max(2rem,var(--safe-area-bottom))] pt-[max(1rem,var(--safe-area-top))] md:px-5 md:pb-5 md:pt-5 lg:px-6 lg:pb-6 lg:pt-6"',
)
shell.write_text(st, encoding="utf-8")

tabs = ROOT / "components/ui/tabs.tsx"
tt = tabs.read_text(encoding="utf-8")
tt = tt.replace(
    '"inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors",',
    '"inline-flex min-h-11 items-center justify-center whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors touch-manipulation",',
)
tabs.write_text(tt, encoding="utf-8")

tg = ROOT / "components/layout/telegram-viewport.tsx"
if not tg.exists():
    tg.write_text("""\"use client\";

import * as React from \"react\";

type TelegramWebApp = {
  ready: () => void;
  expand?: () => void;
  disableVerticalSwipes?: () => void;
};

export function TelegramViewport() {
  React.useEffect(() => {
    const webApp = (window as Window & { Telegram?: { WebApp?: TelegramWebApp } }).Telegram?.WebApp;
    if (!webApp) return;

    webApp.ready();
    webApp.expand?.();
    webApp.disableVerticalSwipes?.();
    document.documentElement.classList.add(\"telegram-webapp\");
  }, []);

  return null;
}
""", encoding="utf-8")

prov = ROOT / "providers/app-providers.tsx"
pt = prov.read_text(encoding="utf-8")
if "TelegramViewport" not in pt:
    pt = pt.replace(
        'import { ThemeProvider } from "@/providers/theme-provider";',
        'import { ThemeProvider } from "@/providers/theme-provider";\nimport { TelegramViewport } from "@/components/layout/telegram-viewport";',
    )
    pt = pt.replace(
        "<SessionExpiredBanner />{children}",
        "<TelegramViewport /><SessionExpiredBanner />{children}",
    )
    prov.write_text(pt, encoding="utf-8")

print("extras ok")
