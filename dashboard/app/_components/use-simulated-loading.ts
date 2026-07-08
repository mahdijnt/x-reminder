"use client";

import * as React from "react";

export function useSimulatedLoading(delayMs = 650) {
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const t = window.setTimeout(() => setLoading(false), delayMs);
    return () => window.clearTimeout(t);
  }, [delayMs]);

  return loading;
}
