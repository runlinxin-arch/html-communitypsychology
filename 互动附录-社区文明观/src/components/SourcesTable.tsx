import { Button, Card, Chip } from "@heroui/react";
import { useState } from "react";

import { citationRules, sourceKinds, sources, type SourceItem, type SourceKind } from "../data";
import { Section } from "./Section";

function SourceCard({ item }: { item: SourceItem }) {
  return (
    <Card className="avoid-break" variant="default">
      <Card.Content className="flex gap-4">
        <span className="font-serif text-sm leading-6 text-accent">
          {String(item.n).padStart(2, "0")}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-[14.5px] leading-[1.85]">{item.title}</p>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-2">
            <Chip size="sm" variant="soft">
              {item.kind}
            </Chip>
            <span className="text-xs text-muted">核证状态：{item.status}</span>
          </div>
          {item.note ? (
            <p className="mt-2 text-xs leading-relaxed text-muted">注意：{item.note}</p>
          ) : null}
          {item.link ? (
            <a
              className="link-is-url mt-2 inline-block break-all text-xs text-link underline decoration-dotted underline-offset-4"
              href={item.link}
              rel="noreferrer"
              target="_blank"
            >
              {item.link}
            </a>
          ) : (
            <p className="mt-2 text-xs text-muted">出处：民政部官网（未附链接）</p>
          )}
        </div>
      </Card.Content>
    </Card>
  );
}

export function SourcesTable() {
  const [kind, setKind] = useState<SourceKind | "全部">("全部");
  const items = kind === "全部" ? sources : sources.filter((item) => item.kind === kind);

  return (
    <Section
      id="sources"
      kicker="附录 · 文档层"
      num="05"
      title="来源与核证状态"
      lead="正文只引教材页码；外延材料一律放在这里，逐条标明性质与核证状态。"
    >
      <div className="mb-5 flex flex-wrap items-center gap-2 print:hidden">
        {(["全部", ...sourceKinds] as const).map((option) => (
          <Button
            key={option}
            size="sm"
            variant={kind === option ? "primary" : "secondary"}
            onPress={() => setKind(option)}
          >
            {option}
            {option !== "全部" ? `（${sources.filter((s) => s.kind === option).length}）` : ""}
          </Button>
        ))}
        <Chip className="ms-1" size="sm" variant="soft">
          共 {items.length} 条
        </Chip>
      </div>

      <div className="space-y-3 print:hidden">
        {items.map((item) => (
          <SourceCard key={item.n} item={item} />
        ))}
      </div>

      <div className="hidden space-y-3 print:block">
        {sources.map((item) => (
          <SourceCard key={item.n} item={item} />
        ))}
      </div>

      <div className="mt-6 rounded-2xl border border-border bg-surface/60 p-5">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">三条引用规则</p>
        <ul className="mt-3 space-y-2">
          {citationRules.map((rule) => (
            <li key={rule} className="flex gap-3 text-[13.5px] leading-[1.85] text-muted">
              <span className="mt-[0.6em] h-px w-4 shrink-0 bg-accent" />
              {rule}
            </li>
          ))}
        </ul>
      </div>
    </Section>
  );
}
