# Next.js & React 19 Patterns & Best Practices

## App Router & Server vs. Client Components
In Next.js App Router (`app/` directory), components are Server Components by default. Add `'use client'` at the top of files that use React hooks (`useState`, `useEffect`, `useCallback`) or browser APIs (`localStorage`, `window`):

```tsx
'use client';

import React, { useState, useEffect } from 'react';

export function InteractiveCounter() {
  const [count, setCount] = useState<number>(0);

  useEffect(() => {
    const saved = localStorage.getItem('kint_counter');
    if (saved) setCount(parseInt(saved, 10));
  }, []);

  const increment = () => {
    const next = count + 1;
    setCount(next);
    localStorage.setItem('kint_counter', next.toString());
  };

  return (
    <button
      onClick={increment}
      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
    >
      Count: {count}
    </button>
  );
}
```

## State Management & LocalStorage Persistence Pattern
Use safe SSR hydration checks when accessing browser APIs like `localStorage` in Next.js:

```tsx
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = (newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error('LocalStorage error:', error);
    }
  };

  return [value, setStoredValue] as const;
}
```

## Resizable Split Panels and Touch Dragging
Implement smooth pointer drag splitters with persistent layout width:

```tsx
export function SplitView({ left, right }: { left: React.ReactNode; right: React.ReactNode }) {
  const [width, setWidth] = useState(400);

  const startResize = (e: React.MouseEvent) => {
    e.preventDefault();
    const handleMove = (moveEvent: MouseEvent) => {
      const newWidth = Math.max(300, Math.min(moveEvent.clientX, window.innerWidth - 300));
      setWidth(newWidth);
    };
    const handleUp = () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
  };

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <div style={{ width: `${width}px` }} className="h-full shrink-0">
        {left}
      </div>
      <div
        onMouseDown={startResize}
        className="w-1 cursor-col-resize bg-zinc-700 hover:bg-blue-500 transition-colors"
      />
      <div className="flex-1 h-full min-w-0">{right}</div>
    </div>
  );
}
```
