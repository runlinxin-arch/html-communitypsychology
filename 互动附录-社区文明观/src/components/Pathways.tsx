import { Accordion, Chip } from "@heroui/react";

import { pathways, type Pathway } from "../data";
import { Section } from "./Section";

function Details({ item }: { item: Pathway }) {
  return (
    <>
      <p className="text-xs text-muted">{item.source}</p>
      <ul className="mt-4 space-y-3">
        {item.points.map((point) => (
          <li key={point.title} className="flex gap-3">
            <span className="mt-[0.62em] h-px w-4 shrink-0 bg-accent" />
            <span className="text-[14.5px] leading-[1.9]">
              <b className="font-medium">{point.title}</b>
              <span className="text-muted"> —— {point.text}</span>
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-5 border-l-2 border-accent pl-4 font-serif text-[16px] leading-[1.9]">
        {item.pull}
      </p>
      {item.image ? (
        <figure className="mt-5 max-w-xl">
          <img
            alt={item.image.alt}
            className="w-full rounded-xl border border-border"
            src={item.image.src}
          />
          <figcaption className="mt-2 text-xs leading-relaxed text-muted">
            {item.image.caption}
          </figcaption>
        </figure>
      ) : null}
    </>
  );
}

export function Pathways() {
  return (
    <Section
      id="pathways"
      kicker="建设途径"
      num="03"
      title="三扇门，怎么一扇一扇打开"
      lead="教材给的建设途径分两层：社区层面两条（环境、知识传播），个人层面一条（文明行为的养成）。展开看每条的要点与出处。"
    >
      <div className="print:hidden">
        <Accordion allowsMultipleExpanded defaultExpandedKeys={["environment"]} variant="surface">
          {pathways.map((item) => (
            <Accordion.Item key={item.id} id={item.id}>
              <Accordion.Heading>
                <Accordion.Trigger>
                  <span className="me-auto text-left">
                    <span className="block text-[11px] uppercase tracking-[0.18em] text-muted">
                      {item.order}
                    </span>
                    <span className="mt-1 block font-serif text-base md:text-lg">{item.title}</span>
                  </span>
                  <Chip className="hidden sm:inline-flex" color="accent" size="sm" variant="soft">
                    {item.subtitle}
                  </Chip>
                  <Accordion.Indicator />
                </Accordion.Trigger>
              </Accordion.Heading>
              <Accordion.Panel>
                <Accordion.Body>
                  <Details item={item} />
                </Accordion.Body>
              </Accordion.Panel>
            </Accordion.Item>
          ))}
        </Accordion>
      </div>

      <div className="hidden space-y-8 print:block">
        {pathways.map((item) => (
          <div key={item.id} className="avoid-break">
            <h3 className="font-serif text-lg">
              {item.order}｜{item.title}（{item.subtitle}）
            </h3>
            <div className="mt-3">
              <Details item={item} />
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}
