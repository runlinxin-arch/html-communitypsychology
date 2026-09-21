import type { ReactNode } from "react";

/** 正文里的教材页码标记。 */
export function PageRef({ children }: { children: ReactNode }) {
  return <span className="pageref">{children}</span>;
}

/** 每个章节统一的开头：编号 · 栏目标签 · 标题 · 导读。 */
export function Section({
  id,
  num,
  kicker,
  title,
  lead,
  children,
}: {
  id: string;
  num: string;
  kicker: string;
  title: string;
  lead?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 border-t border-separator py-14 md:py-16">
      <div className="flex items-center gap-3 text-[11px] uppercase tracking-[0.22em] text-muted">
        <span className="font-serif text-sm tracking-[0.1em] text-accent">{num}</span>
        <span className="h-px w-10 bg-current opacity-40" />
        <span>{kicker}</span>
      </div>
      <h2 className="mt-4 font-serif text-2xl font-semibold leading-snug tracking-tight md:text-[2.1rem]">
        {title}
      </h2>
      {lead ? <p className="mt-4 max-w-3xl text-[15px] leading-[1.9] text-muted">{lead}</p> : null}
      <div className="mt-8">{children}</div>
    </section>
  );
}
