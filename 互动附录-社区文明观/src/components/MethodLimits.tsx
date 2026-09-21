import { Card } from "@heroui/react";

import { divergence, limits, method } from "../data";
import { Section } from "./Section";

export function MethodLimits() {
  return (
    <Section
      id="method"
      kicker="附录 · 自证"
      num="07"
      title="方法与限制"
      lead="一份阅读汇报该交代的两件事：话是从哪来的，以及哪些话还不能说满。"
    >
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="avoid-break" variant="default">
          <Card.Header>
            <Card.Title className="font-serif text-lg">{method.title}</Card.Title>
          </Card.Header>
          <Card.Content>
            <p className="text-[14px] leading-[1.9] text-muted">{method.text}</p>
          </Card.Content>
        </Card>

        <Card className="avoid-break" variant="default">
          <Card.Header>
            <Card.Title className="font-serif text-lg">{limits.title}</Card.Title>
          </Card.Header>
          <Card.Content>
            <p className="text-[14px] leading-[1.9] text-muted">{limits.text}</p>
          </Card.Content>
        </Card>
      </div>

      <Card className="avoid-break mt-4" variant="tertiary">
        <Card.Header>
          <Card.Title className="font-serif text-lg">{divergence.title}</Card.Title>
        </Card.Header>
        <Card.Content>
          <p className="text-[14px] leading-[1.9] text-muted">{divergence.text}</p>
        </Card.Content>
      </Card>
    </Section>
  );
}
