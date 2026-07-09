"use client";

import * as React from "react";

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
    document.documentElement.classList.add("telegram-webapp");
  }, []);

  return null;
}
