"use client";

import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { TableColumn } from "@/types";

export interface DataTableProps<T> {
  columns: TableColumn<T>[];
  rows: T[];
  caption?: string;
  emptyMessage?: string;
  getRowKey?: (row: T, index: number) => string;
  className?: string;
}

export function DataTable<T>({
  columns,
  rows,
  caption,
  emptyMessage = "No rows available.",
  getRowKey,
  className,
}: DataTableProps<T>) {
  return (
    <div className={cn("rounded-2xl border border-glass-border glass-surface p-2 overflow-hidden", className)}>
      <Table>
        {caption ? <TableCaption>{caption}</TableCaption> : null}
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead
                key={String(column.key)}
                className={cn(
                  column.align === "right" && "text-right",
                  column.align === "center" && "text-center"
                )}
              >
                {column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length > 0 ? (
            rows.map((row, rowIndex) => (
              <TableRow key={getRowKey?.(row, rowIndex) ?? String(rowIndex)}>
                {columns.map((column) => {
                  const rawValue = row[column.key as keyof T];
                  return (
                    <TableCell
                      key={String(column.key)}
                      className={cn(
                        column.align === "right" && "text-right",
                        column.align === "center" && "text-center"
                      )}
                    >
                      {column.render ? column.render(row, rowIndex) : String(rawValue ?? "")}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="py-8 text-center text-muted-foreground">
                {emptyMessage}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
