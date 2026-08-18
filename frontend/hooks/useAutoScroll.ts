"use client";

import { useEffect, useRef } from "react";

/**
 * Custom hook to automatically scroll a container element to the bottom
 * whenever its dependencies change.
 */
export function useAutoScroll<T extends HTMLElement>(dependencies: unknown[]) {
  const scrollRef = useRef<T>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return scrollRef;
}
