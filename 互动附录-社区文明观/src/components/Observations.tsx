import { Card, Chip } from "@heroui/react";

import { observationCaveat, observations } from "../data";
import { Section } from "./Section";

export function Observations() {
  return (
    <Section
      id="observations"
      kicker="我住的两个小区"
      num="06"
      title="三行观察"
      lead="这一章讲的都是别人；下面三件是我自己小区里的事。它们只用来对应机制，不用来证明趋势。"
    >
      <div className="space-y-4">
        {observations.map((item) => (
          <Card key={item.n} className="avoid-break" variant="secondary">
            <Card.Content className="flex gap-4">
              <span className="font-serif text-lg leading-none text-accent">{item.n}</span>
              <div className="min-w-0 flex-1">
                <h3 className="font-serif text-[17px] leading-snug">{item.title}</h3>
                <p className="mt-3 text-[14px] leading-[1.9] text-muted">{item.detail}</p>
                <div className="mt-3 flex flex-wrap items-center gap-3">
                  <Chip size="sm" variant="soft">
                    {item.tag}
                  </Chip>
                  <span className="text-xs text-muted">{item.link}</span>
                </div>
              </div>
            </Card.Content>
          </Card>
        ))}
      </div>

      <p className="mt-5 text-xs leading-relaxed text-muted">{observationCaveat}</p>
    </Section>
  );
}
