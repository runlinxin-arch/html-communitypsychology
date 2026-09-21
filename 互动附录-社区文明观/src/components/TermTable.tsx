import { Chip, Table } from "@heroui/react";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";

import { terms, type Term } from "../data";
import { Section } from "./Section";

function Rows({ items }: { items: Term[] }) {
  return (
    <>
      {items.map((term) => (
        <Table.Row key={term.zh} id={term.zh}>
          <Table.Cell className="font-medium">{term.zh}</Table.Cell>
          <Table.Cell className="font-serif">{term.en}</Table.Cell>
          <Table.Cell className="text-xs text-muted">{term.note}</Table.Cell>
        </Table.Row>
      ))}
    </>
  );
}

function TableShell({ children }: { children: ReactNode }) {
  return (
    <Table>
      <Table.ScrollContainer>
        <Table.Content aria-label="术语中英对照" className="min-w-[620px]">
          <Table.Header>
            <Table.Column isRowHeader>中文（教材用语）</Table.Column>
            <Table.Column>英文</Table.Column>
            <Table.Column>备注</Table.Column>
          </Table.Header>
          <Table.Body>{children}</Table.Body>
        </Table.Content>
      </Table.ScrollContainer>
    </Table>
  );
}

export function TermTable() {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) {
      return terms;
    }
    return terms.filter((term) =>
      `${term.zh} ${term.en} ${term.note}`.toLowerCase().includes(q),
    );
  }, [query]);

  return (
    <Section
      id="terms"
      kicker="附录 · 术语"
      num="04"
      title="术语中英对照"
      lead="标准只有一条：教材给过英文的照抄；教材没给英文的，标「通行译法」，不当成教材表述。"
    >
      <div className="mb-5 flex flex-wrap items-center gap-3 print:hidden">
        <input
          aria-label="搜索术语"
          className="w-full max-w-xs rounded-full border border-border bg-field px-4 py-2 text-sm text-field-foreground outline-none placeholder:text-field-placeholder focus:border-accent focus:ring-2 focus:ring-accent/20"
          placeholder="搜索中文或英文"
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <Chip size="sm" variant="soft">
          {filtered.length} / {terms.length} 条
        </Chip>
      </div>

      <div className="print:hidden">
        <TableShell>
          <Rows items={filtered} />
        </TableShell>
      </div>

      <div className="hidden print:block">
        <TableShell>
          <Rows items={terms} />
        </TableShell>
      </div>
    </Section>
  );
}
