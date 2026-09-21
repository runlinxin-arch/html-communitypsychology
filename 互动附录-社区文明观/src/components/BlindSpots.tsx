import { Card, Chip, Tabs } from "@heroui/react";

import { blindSpots, type BlindSpot } from "../data";
import { PageRef, Section } from "./Section";

function Panel({ item }: { item: BlindSpot }) {
  return (
    <div className="avoid-break grid gap-4 md:grid-cols-[1.25fr_0.75fr]">
      <Card variant="secondary">
        <Card.Header>
          <Card.Description className="text-xs tracking-wide text-muted">
            {item.tag} · 教材原文 <PageRef>{item.page}</PageRef>
          </Card.Description>
          <Card.Title className="font-serif text-lg">{item.paperName}</Card.Title>
        </Card.Header>
        <Card.Content>
          <p className="border-l-2 border-accent pl-4 font-serif text-[15.5px] leading-[1.95]">
            {item.quote}
          </p>
          <p className="mt-4 text-[13.5px] leading-[1.85] text-muted">{item.textbook}</p>
        </Card.Content>
      </Card>

      <Card variant="tertiary">
        <Card.Header>
          <Card.Title className="text-sm text-muted">我的读法</Card.Title>
        </Card.Header>
        <Card.Content>
          <p className="font-serif text-[17px] leading-[1.85]">{item.reading}</p>
        </Card.Content>
      </Card>
    </div>
  );
}

export function BlindSpots() {
  return (
    <Section
      id="blindspots"
      kicker="三个矛盾"
      num="02"
      title="书里列的三对矛盾，其实是一件事"
      lead="教材列的是三对矛盾；我把它们读成三扇「看不见」。接下来三组办法，恰好是在把这三扇一扇一扇打开。"
    >
      <div className="print:hidden">
        <Tabs className="w-full">
          <Tabs.ListContainer>
            <Tabs.List aria-label="三扇看不见">
              {blindSpots.map((item) => (
                <Tabs.Tab key={item.id} id={item.id}>
                  {item.label}
                  <Tabs.Indicator />
                </Tabs.Tab>
              ))}
            </Tabs.List>
          </Tabs.ListContainer>
          {blindSpots.map((item) => (
            <Tabs.Panel key={item.id} className="pt-6" id={item.id}>
              <Panel item={item} />
            </Tabs.Panel>
          ))}
        </Tabs>
      </div>

      <div className="hidden space-y-6 print:block">
        {blindSpots.map((item) => (
          <div key={item.id}>
            <h3 className="mb-3 font-serif text-lg">
              {item.label}（{item.paperName}）
            </h3>
            <Panel item={item} />
          </div>
        ))}
      </div>

      <p className="mt-6 text-xs leading-relaxed text-muted">
        三张卡片是教材原文；「我的读法」一栏是汇报人的读法，不是教材表述。<Chip className="ml-1" size="sm" variant="soft">
          教材原文 / 我的读法 已分栏
        </Chip>
      </p>
    </Section>
  );
}
