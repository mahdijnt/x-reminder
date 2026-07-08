"use client";

import * as React from "react";
import { Check, ChevronRight } from "lucide-react";

import { Portal } from "@/components/ui/portal";
import { cn } from "@/lib/utils";

type DropdownMenuContextValue = {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  triggerRef: React.MutableRefObject<HTMLElement | null>;
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
  const triggerRef = React.useRef<HTMLElement | null>(null);
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
    <DropdownMenuContext.Provider value={{ open: resolvedOpen, setOpen, triggerRef }}>
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
  const { open, setOpen, triggerRef } = useDropdownMenuContext();

  const setRefs = React.useCallback(
    (node: HTMLButtonElement | null) => {
      triggerRef.current = node;
      if (typeof ref === "function") ref(node);
      else if (ref) ref.current = node;
    },
    [ref, triggerRef]
  );

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onClick?.(event);
    if (!event.defaultPrevented) {
      setOpen(!open);
    }
  };

  if (asChild && React.isValidElement(children)) {
    const childProps = children.props as Record<string, unknown>;
    const childOnClick = childProps.onClick as
      | ((event: React.MouseEvent<HTMLButtonElement>) => void)
      | undefined;

    return React.cloneElement(children, {
      ...childProps,
      ref: (node: HTMLButtonElement | null) => {
        triggerRef.current = node;
        const childRef = (childProps as { ref?: React.Ref<HTMLButtonElement> }).ref;
        if (typeof childRef === "function") childRef(node);
        else if (childRef && typeof childRef === "object") {
          (childRef as React.MutableRefObject<HTMLButtonElement | null>).current = node;
        }
      },
      onClick: (event: React.MouseEvent<HTMLButtonElement>) => {
        childOnClick?.(event);
        if (!event.defaultPrevented) {
          handleClick(event);
        }
      },
      "aria-expanded": open,
      "aria-haspopup": "menu",
    } as Record<string, unknown>);
  }

  return (
    <button
      ref={setRefs}
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
  sideOffset?: number;
}

export const DropdownMenuContent = React.forwardRef<
  HTMLDivElement,
  DropdownMenuContentProps
>(({ className, align = "end", sideOffset = 8, style, ...props }, ref) => {
  const { open, setOpen, triggerRef } = useDropdownMenuContext();
  const contentRef = React.useRef<HTMLDivElement | null>(null);
  const [position, setPosition] = React.useState({ top: 0, left: 0, minWidth: 192 });

  const updatePosition = React.useCallback(() => {
    const trigger = triggerRef.current;
    if (!trigger) return;

    const rect = trigger.getBoundingClientRect();
    const minWidth = Math.max(rect.width, 192);
    const left = align === "end" ? rect.right - minWidth : rect.left;

    setPosition({
      top: rect.bottom + sideOffset,
      left: Math.max(8, Math.min(left, window.innerWidth - minWidth - 8)),
      minWidth,
    });
  }, [align, sideOffset, triggerRef]);

  React.useLayoutEffect(() => {
    if (!open) return;
    updatePosition();
  }, [open, updatePosition]);

  React.useEffect(() => {
    if (!open) return;

    const handlePointerDown = (event: MouseEvent) => {
      const target = event.target as Node;
      if (contentRef.current?.contains(target)) return;
      if (triggerRef.current?.contains(target)) return;
      setOpen(false);
    };

    const handleReposition = () => updatePosition();

    document.addEventListener("mousedown", handlePointerDown);
    window.addEventListener("resize", handleReposition);
    window.addEventListener("scroll", handleReposition, true);

    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      window.removeEventListener("resize", handleReposition);
      window.removeEventListener("scroll", handleReposition, true);
    };
  }, [open, setOpen, triggerRef, updatePosition]);

  if (!open) return null;

  return (
    <Portal>
      <div
        ref={(node) => {
          contentRef.current = node;
          if (typeof ref === "function") ref(node);
          else if (ref) ref.current = node;
        }}
        role="menu"
        style={{
          position: "fixed",
          top: position.top,
          left: position.left,
          minWidth: position.minWidth,
          zIndex: "var(--z-dropdown)",
          ...style,
        }}
        className={cn(
          "max-h-[min(24rem,calc(100vh-1rem))] overflow-y-auto overflow-x-hidden rounded-lg border border-glass-border bg-popover/95 p-1 text-popover-foreground shadow-glow backdrop-blur-xl animate-ds-in",
          className
        )}
        {...props}
      />
    </Portal>
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
