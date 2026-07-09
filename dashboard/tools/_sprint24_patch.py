from pathlib import Path

ROOT = Path(r"E:/GitHub/x-reminder/dashboard")

def patch_file(rel, old, new, required=True):
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    if old not in t:
        if required:
            raise SystemExit(f"patch miss {rel}: {old[:60]!r}")
        return False
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    return True

# globals
g = ROOT / "app/globals.css"
text = g.read_text(encoding="utf-8")
if "--safe-area-top" not in text:
    text = text.replace(
        "    --container-padding: 1rem;",
        """    --container-padding: 1rem;
    --safe-area-top: env(safe-area-inset-top, 0px);
    --safe-area-right: env(safe-area-inset-right, 0px);
    --safe-area-bottom: env(safe-area-inset-bottom, 0px);
    --safe-area-left: env(safe-area-inset-left, 0px);""",
    )
if ".safe-area-shell" not in text:
    insert = """
  .safe-area-x {
    padding-left: max(var(--container-padding), var(--safe-area-left));
    padding-right: max(var(--container-padding), var(--safe-area-right));
  }

  .safe-area-y {
    padding-top: max(0px, var(--safe-area-top));
    padding-bottom: max(0px, var(--safe-area-bottom));
  }

  .safe-area-shell {
    padding-top: max(0.75rem, var(--safe-area-top));
    padding-bottom: max(2rem, var(--safe-area-bottom));
    padding-left: max(var(--container-padding), var(--safe-area-left));
    padding-right: max(var(--container-padding), var(--safe-area-right));
  }

  .scrollbar-thin-x {
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
  }

  .scrollbar-thin-x::-webkit-scrollbar {
    height: 6px;
  }

  .scrollbar-thin-x::-webkit-scrollbar-thumb {
    border-radius: 9999px;
    background: hsl(var(--muted-foreground) / 0.35);
  }

"""
    text = text.replace("  .skeleton-shimmer {", insert + "  .skeleton-shimmer {")
if "backdrop-filter: blur(12px)" not in text:
    text = text.rstrip() + """

@media (max-width: 767px) {
  .glass-panel,
  .glass-surface,
  .card-premium {
    backdrop-filter: blur(12px) saturate(120%);
    -webkit-backdrop-filter: blur(12px) saturate(120%);
  }

  .aurora-blob {
    filter: blur(48px);
    opacity: 0.32;
  }
}
"""
g.write_text(text, encoding="utf-8")

# layout
layout = ROOT / "app/layout.tsx"
lt = layout.read_text(encoding="utf-8")
if "export const viewport" not in lt:
    lt = lt.replace(
        'import type { Metadata } from "next";',
        'import type { Metadata, Viewport } from "next";',
    )
    lt = lt.replace(
        "export const metadata: Metadata = {",
        """export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export const metadata: Metadata = {""",
    )
    lt = lt.replace(
        '<body className="min-h-screen bg-background text-foreground antialiased">',
        '<body className="min-h-screen min-h-[100dvh] touch-manipulation overflow-x-hidden bg-background text-foreground antialiased">',
    )
    lt = lt.replace("focus:top-4", "focus:top-[max(1rem,var(--safe-area-top))]")
    layout.write_text(lt, encoding="utf-8")

print("patch core ok")
