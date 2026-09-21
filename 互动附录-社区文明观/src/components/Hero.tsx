import { Chip } from "@heroui/react";

import cover from "../assets/cover-scroll.jpg";
import { report } from "../data";

export function Hero() {
  return (
    <header className="mt-6 overflow-hidden rounded-3xl border border-border bg-surface">
      <div className="grid-bg">
        <div className="grid gap-8 p-7 md:grid-cols-[1.15fr_0.85fr] md:p-10">
          <div>
            <p className="text-[11px] uppercase tracking-[0.22em] text-accent">{report.kicker}</p>
            <h1 className="mt-3 font-serif text-3xl font-semibold leading-tight md:text-[2.6rem]">
              {report.title}
            </h1>
            <p className="mt-5 font-serif text-xl leading-snug md:text-2xl">{report.claim}</p>
            <p className="mt-4 max-w-2xl text-sm leading-[1.95] text-muted">{report.lead}</p>

            <div className="mt-6 flex flex-wrap gap-2">
              {["看得见的环境", "看得见的别人", "看得见的将来"].map((tag) => (
                <Chip key={tag} color="accent" size="sm" variant="soft">
                  {tag}
                </Chip>
              ))}
            </div>

            <p className="mt-6 text-xs leading-relaxed text-muted">
              {report.basis}
              <br />
              {report.source}
            </p>
          </div>

          <figure className="avoid-break self-start">
            <img
              alt="本汇报幻灯片封面用图"
              className="w-full rounded-2xl border border-border object-cover"
              src={cover}
            />
            <figcaption className="mt-3 text-xs leading-relaxed text-muted">
              本汇报幻灯片封面用图，在此作装饰，不作史料引用。页面其余图像：卡纳莱托《圣马可广场》，见「建设途径」一栏。
            </figcaption>
          </figure>
        </div>
      </div>
    </header>
  );
}
