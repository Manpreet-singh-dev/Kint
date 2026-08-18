import React from "react";
import { APP_NAME, APP_TAGLINE } from "@/lib/constants";

export interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export function Header({
  title = APP_NAME,
  subtitle = APP_TAGLINE,
}: HeaderProps) {
  return (
    <header className="border-b border-zinc-800 px-6 py-4 bg-zinc-900">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-50 tracking-tight">
            {title}
          </h1>
          <p className="text-sm text-zinc-400 mt-0.5">{subtitle}</p>
        </div>
      </div>
    </header>
  );
}
