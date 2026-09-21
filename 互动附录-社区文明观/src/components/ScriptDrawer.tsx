import { Button, Drawer } from "@heroui/react";

import { scriptPreamble, scriptSections, type ScriptBlock } from "../script";

function Inline({ text }: { text: string }) {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return (
    <>
      {parts.map((part, index) =>
        index % 2 === 1 ? (
          <strong key={index} className="font-semibold text-foreground">
            {part}
          </strong>
        ) : (
          <span key={index}>{part}</span>
        ),
      )}
    </>
  );
}

function Block({ block }: { block: ScriptBlock }) {
  if (block.kind === "quote") {
    return (
      <p className="rounded-xl border border-border bg-default-soft px-4 py-3 text-xs leading-[1.8] text-muted">
        <Inline text={block.text} />
      </p>
    );
  }
  if (block.kind === "bullet") {
    return (
      <p className="flex gap-3 text-[13px] leading-[1.85] text-muted">
        <span className="mt-[0.65em] h-px w-3 shrink-0 bg-accent" />
        <span>
          <Inline text={block.text} />
        </span>
      </p>
    );
  }
  return (
    <p className="text-[14px] leading-[1.95]">
      <Inline text={block.text} />
    </p>
  );
}

export function ScriptDrawer() {
  return (
    <Drawer>
      <Button className="no-print" size="sm" variant="secondary">
        <svg
          aria-hidden="true"
          fill="none"
          height="15"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.6"
          viewBox="0 0 24 24"
          width="15"
        >
          <path d="M4 7h16M4 12h16M4 17h10" />
        </svg>
        讲稿
      </Button>
      <Drawer.Backdrop>
        <Drawer.Content className="w-full max-w-2xl" placement="right">
          <Drawer.Dialog>
            <Drawer.Header>
              <Drawer.Heading className="font-serif text-base">
                讲稿 · 第六章《社区的文明观》
              </Drawer.Heading>
              <Drawer.CloseTrigger />
            </Drawer.Header>
            <Drawer.Body className="space-y-6">
              <div className="rounded-xl border border-border bg-surface-secondary p-4">
                {scriptPreamble.map((block, index) => (
                  <p key={index} className="text-xs leading-[1.8] text-muted">
                    <Inline text={block.text} />
                  </p>
                ))}
              </div>

              {scriptSections.map((section) => (
                <section key={section.id} className="avoid-break">
                  <h3 className="flex flex-wrap items-baseline gap-2 font-serif text-[15px]">
                    {section.name}
                    {section.time ? (
                      <span className="text-xs font-normal tracking-wide text-muted">
                        {section.time}
                      </span>
                    ) : null}
                  </h3>
                  <div className="mt-3 space-y-3">
                    {section.blocks.map((block, index) => (
                      <Block key={index} block={block} />
                    ))}
                  </div>
                </section>
              ))}
            </Drawer.Body>
            <Drawer.Footer>
              <Button slot="close" size="sm" variant="secondary">
                关闭
              </Button>
            </Drawer.Footer>
          </Drawer.Dialog>
        </Drawer.Content>
      </Drawer.Backdrop>
    </Drawer>
  );
}
