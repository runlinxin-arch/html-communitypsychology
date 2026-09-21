import { Button, ProgressBar, useTheme } from "@heroui/react";
import { useEffect, useState } from "react";

import { BlindSpots } from "./components/BlindSpots";
import { ChapterMap } from "./components/ChapterMap";
import { Hero } from "./components/Hero";
import { MethodLimits } from "./components/MethodLimits";
import { Observations } from "./components/Observations";
import { Pathways } from "./components/Pathways";
import { ScriptDrawer } from "./components/ScriptDrawer";
import { SourcesTable } from "./components/SourcesTable";
import { TermTable } from "./components/TermTable";

const nav = [
  { href: "#map", label: "本章地图" },
  { href: "#blindspots", label: "三扇看不见" },
  { href: "#pathways", label: "建设途径" },
  { href: "#terms", label: "术语对照" },
  { href: "#sources", label: "来源核证" },
  { href: "#observations", label: "三行观察" },
  { href: "#method", label: "方法与限制" },
];

/** 顶部阅读进度条：滚动百分比。 */
function useScrollProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let frame = 0;
    const update = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const el = document.documentElement;
        const max = el.scrollHeight - el.clientHeight;
        setProgress(max > 0 ? Math.min(100, Math.max(0, (el.scrollTop / max) * 100)) : 0);
      });
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, []);

  return progress;
}

function IconSun() {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height="16"
      stroke="currentColor"
      strokeLinecap="round"
      strokeWidth="1.6"
      viewBox="0 0 24 24"
      width="16"
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

function IconMoon() {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height="16"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.6"
      viewBox="0 0 24 24"
      width="16"
    >
      <path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
    </svg>
  );
}

function IconPrint() {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height="16"
      stroke="currentColor"
      strokeLinejoin="round"
      strokeWidth="1.6"
      viewBox="0 0 24 24"
      width="16"
    >
      <path d="M6 9V3h12v6" />
      <rect height="7" rx="2" width="16" x="4" y="9" />
      <path d="M8 16h8v5H8z" />
    </svg>
  );
}

export default function App() {
  const { resolvedTheme, setTheme } = useTheme("dark");
  const progress = useScrollProgress();
  const isDark = (resolvedTheme ?? "dark") !== "light";

  return (
    <div className="min-h-screen">
      <div className="sticky top-0 z-40 no-print">
        <ProgressBar aria-label="阅读进度" className="block" value={progress}>
          <ProgressBar.Track className="h-[3px] rounded-none bg-transparent">
            <ProgressBar.Fill className="bg-accent transition-[width] duration-150" />
          </ProgressBar.Track>
        </ProgressBar>

        <div className="border-b border-separator bg-background/85 backdrop-blur">
          <div className="mx-auto flex max-w-5xl items-center gap-3 px-5 py-3 md:px-8">
            <span className="font-serif text-[13px] leading-tight text-muted">
              第六章《社区的文明观》· 互动附录
            </span>

            <nav className="ml-auto hidden items-center gap-0.5 lg:flex">
              {nav.map((item) => (
                <a
                  key={item.href}
                  className="rounded-full px-2.5 py-1.5 text-xs text-muted transition-colors hover:bg-default hover:text-foreground"
                  href={item.href}
                >
                  {item.label}
                </a>
              ))}
            </nav>

            <div className="ml-auto flex items-center gap-2 lg:ml-3">
              <ScriptDrawer />
              <Button
                isIconOnly
                aria-label={isDark ? "切换到浅色主题" : "切换到深色主题"}
                size="sm"
                variant="ghost"
                onPress={() => setTheme(isDark ? "light" : "dark")}
              >
                {isDark ? <IconSun /> : <IconMoon />}
              </Button>
              <Button
                isIconOnly
                aria-label="打印或导出 PDF"
                size="sm"
                variant="ghost"
                onPress={() => window.print()}
              >
                <IconPrint />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-5 pb-4 md:px-8">
        <Hero />
        <ChapterMap />
        <BlindSpots />
        <Pathways />
        <TermTable />
        <SourcesTable />
        <Observations />
        <MethodLimits />
      </div>

      <footer className="mt-8 border-t border-separator py-10">
        <div className="mx-auto max-w-5xl px-5 text-xs leading-relaxed text-muted md:px-8">
          <p>
            本页是《社区文明观-阅读汇报.html》（14 页幻灯片）的配套互动附录：幻灯片负责讲，这一页负责查。
            两边的口径、页码与用词一致；讲稿全文见顶部「讲稿」按钮。
          </p>
          <p className="mt-3">
            打印或导出 PDF 时：折叠与切换的内容会自动展开，页眉页脚与按钮不打印，正文里的外链会自动附出网址。
          </p>
          <p className="mt-3">
            教材基准文本：第 124–148 页（25 页扫描件逐字核对）。外延材料的核证状态见「来源与核证状态」一栏。
          </p>
        </div>
      </footer>
    </div>
  );
}
