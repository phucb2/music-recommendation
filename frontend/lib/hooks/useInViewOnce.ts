"use client";

import { useEffect, useRef } from "react";

/**
 * Fires callback once when the element intersects the viewport (IntersectionObserver).
 */
export function useInViewOnce(onVisible: () => void, options?: IntersectionObserverInit) {
  const ref = useRef<HTMLDivElement | null>(null);
  const fired = useRef(false);
  const cbRef = useRef(onVisible);

  useEffect(() => {
    cbRef.current = onVisible;
  }, [onVisible]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const obs = new IntersectionObserver(
      (entries) => {
        const e = entries[0];
        if (!e?.isIntersecting || fired.current) return;
        fired.current = true;
        cbRef.current();
        obs.disconnect();
      },
      { threshold: options?.threshold ?? 0.35, root: options?.root, rootMargin: options?.rootMargin },
    );

    obs.observe(el);
    return () => obs.disconnect();
  }, [options?.root, options?.rootMargin, options?.threshold]);

  return ref;
}
