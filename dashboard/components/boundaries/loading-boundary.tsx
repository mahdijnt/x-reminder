"use client";

import * as React from "react";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";

type LoadingBoundaryProps = {
  isLoading: boolean;
  children: React.ReactNode;
  fallback?: React.ReactNode;
};

export function LoadingBoundary({ isLoading, children, fallback }: LoadingBoundaryProps) {
  if (isLoading) {
    return (
      fallback ?? (
        <div className="space-y-3">
          <LoadingSkeleton lines={4} />
          <LoadingSkeleton lines={4} />
        </div>
      )
    );
  }

  return <>{children}</>;
}

export function withLoadingBoundary<P extends object>(
  Component: React.ComponentType<P>,
  options?: { fallback?: React.ReactNode }
) {
  return function Wrapped(props: P & { isLoading?: boolean }) {
    const { isLoading, ...rest } = props;
    return (
      <LoadingBoundary isLoading={Boolean(isLoading)} fallback={options?.fallback}>
        <Component {...(rest as P)} />
      </LoadingBoundary>
    );
  };
}
