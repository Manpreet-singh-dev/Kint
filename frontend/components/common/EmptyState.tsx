import React, { ReactNode } from "react";

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  children?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  children,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center py-16 text-center ${className}`}
    >
      {icon && (
        <div className="rounded-full bg-zinc-800 p-6 text-zinc-500">{icon}</div>
      )}
      <h2 className="mt-6 text-lg font-medium text-zinc-50">{title}</h2>
      <p className="mt-2 max-w-sm text-sm text-zinc-400 leading-relaxed">
        {description}
      </p>
      {children && <div className="mt-6">{children}</div>}
    </div>
  );
}
