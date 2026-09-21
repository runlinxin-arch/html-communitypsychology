import raw from "./讲稿.md?raw";

export type ScriptBlock = { kind: "p" | "quote" | "bullet"; text: string };
export type ScriptSection = { id: string; name: string; time: string; blocks: ScriptBlock[] };

function parseBlocks(chunk: string): ScriptBlock[] {
  const blocks: ScriptBlock[] = [];
  let buf: string[] = [];
  let kind: "p" | "quote" = "p";

  const flush = () => {
    if (!buf.length) {
      return;
    }
    const text = buf.join(" ").replace(/\s+/g, " ").trim();
    buf = [];
    const current = kind;
    kind = "p";
    if (!text) {
      return;
    }
    blocks.push({ kind: current, text });
  };

  for (const rawLine of chunk.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line === "---") {
      flush();
      continue;
    }
    if (line.startsWith("> ")) {
      if (kind !== "quote") {
        flush();
        kind = "quote";
      }
      buf.push(line.slice(2));
      continue;
    }
    if (line.startsWith("- ")) {
      flush();
      blocks.push({ kind: "bullet", text: line.slice(2) });
      continue;
    }
    kind = "p";
    buf.push(line);
  }
  flush();
  return blocks;
}

const parts = raw.split(/^## /m);
const preambleRaw = parts.shift() ?? "";

export const scriptPreamble = parseBlocks(preambleRaw.split("\n").slice(1).join("\n"));

export const scriptSections: ScriptSection[] = parts.map((part) => {
  const [headLine = "", ...rest] = part.split("\n");
  const [name = "", time = ""] = headLine.split("｜").map((s) => s.trim());
  return {
    id: name.replace(/\s+/g, "-") || "section",
    name,
    time,
    blocks: parseBlocks(rest.join("\n")),
  };
});
