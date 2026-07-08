"use client";

import * as React from "react";
import { Check, ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";

type DropdownMenuContextValue = {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
};

const DropdownMenuContext = React.createContext<DropdownMenuContextValue | null>(null);

function useDropdownMenuContext() {
  const context = React.useContext(DropdownMenuContext);

  if (!context) {
    throw new Error("Dropdown menu components must be used within DropdownMenu.");
  }

  return context;
}

export interface DropdownMenuProps {
  children: React.ReactNode;
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function DropdownMenu({
  children,
  open,
  defaultOpen = false,
  onOpenChange,
}: DropdownMenuProps) {
  const [uncontrolledOpen, setUncontrolledOpen] = React.useState(defaultOpen);
  const isControlled = open !== undefined;
  const resolvedOpen = isControlled ? open : uncontrolledOpen;

  const setOpen = React.useCallback(
    (value: React.SetStateAction<boolean>) => {
      const nextOpen = typeof value === "function" ? value(resolvedOpen) : value;
      if (!isControlled) {
        setUncontrolledOpen(nextOpen);
      }
      onOpenChange?.(nextOpen);
    },
    [isControlled, onOpenChange, resolvedOpen]
  );

  return (
    <DropdownMenuContext.Provider value={{ open: resolvedOpen, setOpen }}>
      <div className="relative inline-flex">{children}</div>
    </DropdownMenuContext.Provider>
  );
}

export interface DropdownMenuTriggerProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
}

export const DropdownMenuTrigger = React.forwardRef<
  HTMLButtonElement,
  DropdownMenuTriggerProps
>(({ className, children, onClick, asChild = false, ...props }, ref) => {
  const { open, setOpen } = useDropdownMenuContext();

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onClick?.(event);
    if (!event.defaultPrevented) {
      setOpen(!open);
    }
  };

  if (asChild && React.isValidElement(children)) {
    const childProps = children.props as Record<string, unknown>;
    const childOnClick = childProps.onClick as ((event: React.MouseEvent<HTMLButtonElement>) => void) | undefined;

    return React.cloneElement(children, {
      ...childProps,
      onClick: (event: React.MouseEvent<HTMLButtonElement>) => {
        childOnClick?.(event);
        if (!event.defaultPrevented) {
          handleClick(event);
        }
      },
      "aria-expanded": open,
      "aria-haspopup": "menu",
    });
  }

  return (
    <button
      ref={ref}
      type="button"
      className={cn("inline-flex", className)}
      aria-expanded={open}
      aria-haspopup="menu"
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  );
});
DropdownMenuTrigger.displayName = "DropdownMenuTrigger";

export interface DropdownMenuContentProps
  extends React.HTMLAttributes<HTMLDivElement> {
  align?: "start" | "end";
}

export const DropdownMenuContent = React.forwardRef<
  HTMLDivElement,
  DropdownMenuContentProps
>(({ className, align = "end", ...props }, ref) => {
  const { open, setOpen } = useDropdownMenuContext();
  const contentRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!open) return;

    const handlePointerDown = (event: MouseEvent) => {
      if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, [open, setOpen]);

  if (!open) return null;

  return (
    <div
      ref={(node) => {
        contentRef.current = node;
        if (typeof ref === "function") ref(node);
        else if (ref) ref.current = node;
      }}
      role="menu"
      className={cn(
        "absolute top-full z-50 mt-2 min-w-[12rem] overflow-hidden rounded-lg border border-glass-border bg-popover/95 p-1 text-popover-foreground shadow-glow backdrop-blur-xl",
        align === "end" ? "right-0" : "left-0",
        className
      )}
      {...props}
    />
  );
});
DropdownMenuContent.displayName = "DropdownMenuContent";

export const DropdownMenuLabel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("px-2 py-1.5 text-sm font-semibold", className)} {...props} />
));
DropdownMenuLabel.displayName = "DropdownMenuLabel";

export const DropdownMenuSeparator = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("-mx-1 my-1 h-px bg-border/70", className)} {...props} />
));
DropdownMenuSeparator.displayName = "DropdownMenuSeparator";

export interface DropdownMenuItemProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  inset?: boolean;
  shortcut?: string;
}

export const DropdownMenuItem = React.forwardRef<
  HTMLButtonElement,
  DropdownMenuItemProps
>(({ className, inset, shortcut, children, ...props }, ref) => {
  const { setOpen } = useDropdownMenuContext();

  return (
    <button
      ref={ref}
      type="button"
      role="menuitem"
      className={cn(
        "relative flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm outline-none transition-colors hover:bg-secondary/60 hover:text-foreground disabled:pointer-events-none disabled:opacity-50",
        inset && "pl-8",
        className
      )}
      onClick={(event) => {
        props.onClick?.(event);
        if (!event.defaultPrevented) {
          setOpen(false);
        }
      }}
      {...props}
    >
      {children}
      {shortcut ? <span className="ml-auto text-xs text-muted-foreground">{shortcut}</span> : null}
    </button>
  );
});
DropdownMenuItem.displayName = "DropdownMenuItem";

export interface DropdownMenuCheckboxItemProps extends DropdownMenuItemProps {
  checked?: boolean;
}

export const DropdownMenuCheckboxItem = React.forwardRef<
  HTMLButtonElement,
  DropdownMenuCheckboxItemProps
>(({ className, checked = false, children, ...props }, ref) => (
  <DropdownMenuItem ref={ref} className={cn("pl-8", className)} {...props}>
    <span className="absolute left-2 inline-flex h-4 w-4 items-center justify-center">
      {checked ? <Check className="h-4 w-4" /> : null}
    </span>
    {children}
  </DropdownMenuItem>
));
DropdownMenuCheckboxItem.displayName = "DropdownMenuCheckboxItem";

export const DropdownMenuSubTrigger = React.forwardRef<
  HTMLButtonElement,
  DropdownMenuItemProps
>(({ children, ...props }, ref) => (
  <DropdownMenuItem ref={ref} {...props}>
    <span className="flex-1 text-left">{children}</span>
    <ChevronRight className="h-4 w-4 text-muted-foreground" />
  </DropdownMenuItem>
));
DropdownMenuSubTrigger.displayName = "DropdownMenuSubTrigger";
