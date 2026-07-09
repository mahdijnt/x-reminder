"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";

type ErrorBoundaryProps = { children: React.ReactNode; fallback?: React.ReactNode; onError?: (error: Error, stack?: string) => void; };
type ErrorBoundaryState = { hasError: boolean; error: Error | null; };

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };
  static getDerivedStateFromError(error: Error): ErrorBoundaryState { return { hasError: true, error }; }
  componentDidCatch(error: Error, info: React.ErrorInfo) { this.props.onError?.(error, info.componentStack ?? undefined); }
  private reset = () => { this.setState({ hasError: false, error: null }); };
  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 p-6 text-center"><p className="text-sm font-medium text-foreground">Something went wrong.</p><p className="max-w-md text-xs text-muted-foreground">{this.state.error?.message}</p><Button type="button" variant="outline" onClick={this.reset}>Try again</Button></div>;
    }
    return this.props.children;
  }
}
