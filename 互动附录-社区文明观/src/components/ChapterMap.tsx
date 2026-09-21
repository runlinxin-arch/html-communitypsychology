import { Card, Chip } from "@heroui/react";

import { concepts, pageIndex, traits } from "../data";
import { PageRef, Section } from "./Section";

export function ChapterMap() {
  return (
    <Section
      id="map"
      kicker="本章地图"
      num="01"
      title="三个词，一层套一层"
      lead="教材这一章的架子是三个词：文明、文明观、社区文明观。落到社区，才成为可以谈「建设」的对象。"
    >
      <div className="grid gap-4 md:grid-cols-3">
        {concepts.map((concept) => (
          <Card key={concept.term} className="avoid-break" variant="default">
            <Card.Header>
              <Card.Title className="font-serif text-lg">{concept.term}</Card.Title>
              <Card.Description className="text-xs tracking-wide text-muted">
                {concept.en} · <PageRef>{concept.page}</PageRef>
              </Card.Description>
            </Card.Header>
            <Card.Content>
              <p className="text-sm leading-[1.9]">{concept.text}</p>
            </Card.Content>
          </Card>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <span className="text-xs text-muted">
          四个特性 <PageRef>{traits.page}</PageRef>
        </span>
        {traits.items.map((trait) => (
          <Chip key={trait} color="accent" size="sm" variant="soft">
            {trait}
          </Chip>
        ))}
      </div>
      <p className="mt-3 max-w-3xl text-sm leading-[1.95] text-muted">{traits.reading}</p>

      <div className="mt-8 rounded-2xl border border-border bg-surface/60 p-5">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">幻灯片页码 → 教材页码</p>
        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2">
          {pageIndex.map((row) => (
            <span key={row.page} className="text-[13px] text-muted">
              {row.page} <span className="text-accent">→</span> <PageRef>{row.ref}</PageRef>
            </span>
          ))}
        </div>
      </div>
    </Section>
  );
}
