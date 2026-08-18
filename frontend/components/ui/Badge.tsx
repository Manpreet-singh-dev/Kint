import React, { HTMLAttributes } from "react";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "user" | "ai" | "neutral";
}

export function Badge({
  children,
  variant = "neutral",
  className = "",
  ...props
}: BadgeProps) {
  const variantStyles = {
    user: "bg-zinc-700 text-zinc-200",
    ai: "bg-zinc-100 text-zinc-900",
    neutral: "bg-zinc-800 text-zinc-400 border border-zinc-700",
  };

  return (
    <span
      className={`inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
