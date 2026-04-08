const COMPANY = "Group 8";

const AUTHORS: { name: string; id: string }[] = [
  { name: "Lưu Trọng Tơ", id: "2570802" },
  { name: "Bùi Bá Phúc", id: "2570799" },
  { name: "Nguyễn Bá Nam", id: "2570795" },
];

type Props = {
  /** Tighter typography for the full-height player. */
  compact?: boolean;
  className?: string;
};

export function SiteFooter({ compact, className = "" }: Props) {
  return (
    <footer
      role="contentinfo"
      className={`relative border-t border-white/[0.06] bg-gradient-to-b from-transparent to-black/20 ${compact ? "shrink-0 px-4 py-2.5" : "px-6 py-6 sm:px-8 sm:py-8"} ${className}`}
    >
      {/* Hairline accent — stage-light cue */}
      <div
        className={`mx-auto rounded-full bg-gradient-to-r from-transparent via-accent/45 to-transparent ${compact ? "mb-2 h-px max-w-[6rem]" : "mb-4 h-[2px] max-w-[7rem] sm:max-w-[9rem]"}`}
        aria-hidden
      />

      <div
        className={`mx-auto max-w-5xl text-center leading-relaxed ${compact ? "text-[10px] sm:text-[11px]" : "text-xs sm:text-sm"}`}
      >
        <span className={`inline font-display font-semibold text-foreground ${compact ? "text-sm sm:text-base" : "text-base sm:text-lg"}`}>
          {COMPANY}
        </span>
        <span className="inline select-none text-accent/35" aria-hidden>
          {" "}
          ·{" "}
        </span>
        <span
          className={`inline font-medium uppercase tracking-[0.18em] text-muted/55 ${compact ? "text-[8px] sm:text-[9px]" : "text-[9px] sm:text-[10px]"}`}
        >
          Authors
        </span>
        {AUTHORS.map((a) => (
          <span key={a.id} className="inline">
            <span className="inline select-none text-accent/25" aria-hidden>
              {" "}
              ·{" "}
            </span>
            <span className="text-muted/90">
              <span className="text-foreground/90">{a.name}</span>
              <span className="ml-1 inline-block rounded bg-white/[0.04] px-1 py-px font-mono text-[0.85em] tabular-nums text-muted/75 ring-1 ring-white/[0.06]">
                {a.id}
              </span>
            </span>
          </span>
        ))}
      </div>
    </footer>
  );
}
