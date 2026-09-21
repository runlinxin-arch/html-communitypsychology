/**
 * 互动附录的全部内容。
 * 口径与《社区文明观-阅读汇报.html》《讲稿-社区文明观-阅读汇报.md》《资料包-第06章汇报.md》一致：
 * 教材主张只写教材原意并附页码；外延材料标注核证状态；个人观察明确声明样本限制。
 */

import canalettoUrl from "./assets/canaletto-san-marco.jpg";

export const report = {
  kicker: "阅读汇报 · 互动附录",
  title: "第六章《社区的文明观》",
  claim: "文明不靠自觉，靠「看得见」。",
  lead: "环境、别人、将来——教材的证据说明现代社区正在把这三样逐一拆掉；所以出路不是多贴标语，而是把「看得见」重新造出来。",
  basis: "基准文本：教材第 124–148 页（25 页扫描件逐字核对）",
  source: "配套文件：《社区文明观-阅读汇报.html》（14 页幻灯片）、《讲稿-社区文明观-阅读汇报.md》",
};

export type Concept = {
  term: string;
  en: string;
  page: string;
  text: string;
};

export const concepts: Concept[] = [
  {
    term: "文明",
    en: "civility",
    page: "p.124–125",
    text: "文化所达到的一个高级层次。文化无先进落后之分，文明则超越阶级性、民族性与地域性；文化可以向下，文明的动态变化向上。",
  },
  {
    term: "文明观",
    en: "view of civilization",
    page: "p.129–130",
    text: "对优秀文化成果所持有的信念和看法。社会层面表现为相互仿效传播的社会风气，个人层面是内化了的价值观。",
  },
  {
    term: "社区文明观",
    en: "view of community civility",
    page: "p.130",
    text: "生活、工作在社区中的人们，对社区文明程度有关的信念和看法。教材把它放在交际语言、生活方式、风俗习惯、历史传统、民间规约的交互里来讲。",
  },
];

export const traits = {
  items: ["指引性", "评价性", "综合性", "交互性"],
  page: "p.131",
  reading: "四个特性里有三个都在说同一件事：看得见。别人看得见你，你也看得见别人，评价才有载体。",
};

export type BlindSpot = {
  id: string;
  label: string;
  tag: string;
  paperName: string;
  page: string;
  quote: string;
  textbook: string;
  reading: string;
};

export const blindSpots: BlindSpot[] = [
  {
    id: "knowledge",
    label: "看不见知识",
    tag: "第一扇",
    paperName: "愚昧与科学",
    page: "p.137",
    quote: "愚昧＝缺乏知识、不明事理，容易轻信谣言、偏爱道听途说。",
    textbook: "教材给出的化解方向是提高受教育水平。",
    reading: "判断的成本被转给了谣言：不是不知道该怎么做，是无从知道。",
  },
  {
    id: "others",
    label: "看不见他人",
    tag: "第二扇",
    paperName: "个人利益与公共利益",
    page: "p.138",
    quote:
      "居住方式从宗族聚集、彼此熟悉、沾亲带故发展到左邻右舍都是陌生人，陌生人社区逐渐增多；社区成员之间长期的重复性博弈减少了。",
    textbook: "教材把原因落在居住方式的变化上，而不是落在个人品德上。",
    reading: "看不见他人，公共利益就守不住。",
  },
  {
    id: "future",
    label: "看不见将来",
    tag: "第三扇",
    paperName: "短期利益与长期利益",
    page: "p.138",
    quote: "深夜播放高音量音乐、高空抛掷垃圾、随意丢弃有害垃圾。",
    textbook: "教材用的是「用短期的方便，换长期的代价」这一类例子。",
    reading: "把成本推给以后的自己和别人。",
  },
];

export type PathwayPoint = { title: string; text: string };

export type Pathway = {
  id: string;
  order: string;
  title: string;
  subtitle: string;
  source: string;
  points: PathwayPoint[];
  pull: string;
  image?: { src: string; alt: string; caption: string };
};

export const pathways: Pathway[] = [
  {
    id: "environment",
    order: "第一扇门",
    title: "把环境收拾干净",
    subtitle: "看得见的环境",
    source: "教材建设途径·社区①：物理环境的整洁有序（p.140、144–145）",
    points: [
      {
        title: "环境的洁净程度会影响个体的道德行为",
        text: "难闻的气味、令人生厌的环境会提高道德上的严苛程度；空气清新会促使个体保持整洁有序，更可能表现出互惠与慈善。",
      },
      {
        title: "无序传递的是信息",
        text: "「无人关心、无人管控、不负后果」。教材把社区物理环境说成一条信息传递通道：及时维护传递出该社区具有较好的控制力。",
      },
      {
        title: "破窗理论",
        text: "一扇窗户坏了没人修，其他窗户很快也会被损坏——因为损坏本身表明没人在乎。",
      },
      {
        title: "有实验证据",
        text: "乱扔垃圾、乱停自行车等造成的无序环境，容易诱发出偷窃这类不法行为。",
      },
    ],
    pull: "管理混乱、脏乱差的社区里，人们会说「扔了就扔了吧，也没什么大不了的」。",
    image: {
      src: canalettoUrl,
      alt: "卡纳莱托《圣马可广场》",
      caption:
        "卡纳莱托《圣马可广场》，1720 年代末，大都会艺术博物馆，公共领域。一个被持续维护的公共空间：铺装、廊柱、人流——环境本身在告诉人该怎么做。",
    },
  },
  {
    id: "rules",
    order: "第二扇门",
    title: "把别人怎么做露出来",
    subtitle: "看得见的别人",
    source: "教材建设途径·社区②：科学文化知识的传播（p.145–146）",
    points: [
      {
        title: "描述性规则：大多数人是怎么做的",
        text: "影响方式类似从众——大多数人怎么做，我就怎么做，靠模仿、复制别人的行为起作用；维持积极行为比命令性规则更有效。",
      },
      {
        title: "命令性规则：应该怎么做",
        text: "它和社会评价绑在一起，奖惩机制在其中起重要作用；遵守时人会更多地考虑他人和社会的评价。",
      },
      {
        title: "用电量反馈的案例",
        text: "告知居民自己家和所在社区的日均用电量，可能促使耗电多的家庭减少消耗，也可能促使耗电少的家庭增加消耗；此时用表示赞赏的笑脸图标起到的道德奖赏作用，可以继续维持低消耗家庭的低用电量。",
      },
      {
        title: "还有一条：传播客观规律知识",
        text: "讲清楚为什么与人为善、为什么要维护生态，让规则从「被要求」变成「被理解」。",
      },
    ],
    pull: "命令性规则要生效，得有人在看；描述性规则只要求一件事——你能看见别人。",
  },
  {
    id: "future",
    order: "第三扇门",
    title: "把将来的自己拉近",
    subtitle: "看得见的将来",
    source: "教材建设途径·个人文明行为的养成（p.142–144）",
    points: [
      {
        title: "转变动机",
        text: "从「不得不讲文明」转变为「我想要讲文明」。做不想做的事，体验到的价值和绩效都更低；出于自己选择时，投入的努力更多。",
      },
      {
        title: "换位思考",
        text: "道德事件发生在时空上较远时，人更容易做出功利的判断；较近时，才更容易把别人的得失看成自己的得失。观点采择能拉近人与人之间的心理距离。",
      },
      {
        title: "培养远见卓识",
        text: "人会把现在的自己看成付出者、把未来的自己看成受益者，于是低估未来的结果，产生短视行为。未来情景预见、自我控制与延迟满足，可以把现在与未来拉近。",
      },
      {
        title: "提升进取心",
        text: "希望、热情、自信、勇气；让居民参与文明社区建设的问题发现与问题解决，把决策权交给最了解社区的人。",
      },
      {
        title: "补充：角色榜样与社会学习",
        text: "教材另给了一条——角色榜样和社会学习；互惠原则也能促进友善行为。",
      },
    ],
    pull: "把将来的自己拉近到现在：人只有看得见将来，才会替将来买单。",
  },
];

export type Term = { zh: string; en: string; note: string };

export const terms: Term[] = [
  { zh: "文明", en: "civility", note: "教材给出的英文，p.125" },
  { zh: "文化", en: "culture", note: "教材给出的英文，p.125" },
  { zh: "文明观", en: "view of civilization", note: "教材给出的英文，p.129" },
  { zh: "社区文明观", en: "view of community civility", note: "教材给出的英文，p.130" },
  { zh: "社会风气", en: "social custom", note: "教材给出的英文，p.141" },
  { zh: "自信", en: "self-confidence", note: "教材给出的英文，p.134" },
  { zh: "环保意识", en: "environmental awareness", note: "教材给出的英文，p.135" },
  { zh: "社会学习", en: "social learning", note: "教材给出的英文，p.147" },
  {
    zh: "描述性规则",
    en: "descriptive norms（通行译法）",
    note: "教材正文只有中文，p.145；英文为通用译名，非教材表述",
  },
  {
    zh: "命令性规则",
    en: "injunctive norms（通行译法）",
    note: "教材正文只有中文，p.145；英文为通用译名，非教材表述",
  },
  {
    zh: "破窗理论",
    en: "broken windows theory（通行译法）",
    note: "教材正文只有中文，p.145；英文为通用译名，非教材表述",
  },
  {
    zh: "观点采择",
    en: "perspective taking（通行译法）",
    note: "教材正文只有中文，p.143；英文为通用译名，非教材表述",
  },
];

export type SourceKind = "古籍" | "法条与政策" | "官方名录" | "期刊";

export type SourceItem = {
  n: number;
  title: string;
  kind: SourceKind;
  status: string;
  note?: string;
  link?: string;
};

export const sourceKinds: SourceKind[] = ["古籍", "法条与政策", "官方名录", "期刊"];

export const sources: SourceItem[] = [
  {
    n: 1,
    title:
      "吕大钧（定稿）、吕大忠（署名）：《吕氏乡约》，宋熙宁九年十二月初五日（1076），京兆府蓝田县。四条＝德业相劝、过失相规、礼俗相交、患难相恤",
    kind: "古籍",
    status: "已核（与《宋史》卷 340 原文比对）",
    note: "引用写《宋史》卷 340；维基类页面只作线索，不作引用",
    link: "https://zh.wikisource.org/wiki/宋史_(四庫全書本)/卷340",
  },
  {
    n: 2,
    title: "《永乐大典》本《乡约》（含《吕氏乡约》全文与朱熹 1175 年识语）",
    kind: "古籍",
    status: "二手转述，链接可查",
    link: "https://www.shidianguji.com/book/YLDD00001/chapter/1lmfjq3458xdy",
  },
  {
    n: 3,
    title: "朱熹《增损吕氏乡约》，《晦庵先生朱文公文集》卷七十四",
    kind: "古籍",
    status: "已核卷次",
    note: "不要写成《朱子家礼》",
    link: "https://www.shidianguji.com/book/NA12033/chapter/1m83nzubsm2w2",
  },
  {
    n: 4,
    title: "王守仁《南赣乡约》，明正德十三年（1518）十月，《王阳明全集》",
    kind: "古籍",
    status: "年代中高",
    note: "卷次随版本而异（上古 1992 本卷十七；识典本编在卷十九「公移二」），引用必须注明版本",
    link: "https://www.shidianguji.com/book/HY0775/chapter/1mb8exhm5hhka",
  },
  {
    n: 5,
    title: "国家级非遗「规约习俗（吕氏乡约乡仪）」，编号 Ⅹ-142，2021 年第五批，申报地陕西蓝田",
    kind: "官方名录",
    status: "已核",
    link: "https://www.ihchina.cn/project_details/23900",
  },
  {
    n: 6,
    title: "《中华人民共和国城市居民委员会组织法》第二条、第三十条、第三十一条",
    kind: "法条与政策",
    status: "已核：1989 制定、2018 修正、2025-10-28 修订、2026-01-01 施行",
    note: "第三十条为居民会议制定或修改居民公约，第三十一条为备案与合法性限制",
    link: "https://www.xinhuanet.com/20251029/29af4ef2b04f43f68bad659009bbeaf7/c.html",
  },
  {
    n: 7,
    title: "民政部等七部门《关于做好村规民约和居民公约工作的指导意见》（民发〔2018〕144 号）",
    kind: "法条与政策",
    status: "已核表述",
    note: "出处为民政部官网",
  },
  {
    n: 8,
    title:
      "Wilson, J. Q., & Kelling, G. L. (1982). Broken Windows. The Atlantic Monthly, 249(3), 29–36, 38.",
    kind: "期刊",
    status: "已核（NCJRS 著录）",
    link: "https://ojp.gov/ncjrs/virtual-library/abstracts/broken-windows",
  },
  {
    n: 9,
    title: "Keizer, K., Lindenberg, S., & Steg, L. (2008). The spreading of disorder. Science, 322(5908), 1681–1685.",
    kind: "期刊",
    status: "已核（PMID 19023045）",
    link: "https://doi.org/10.1126/science.1161405",
  },
  {
    n: 10,
    title:
      "Schultz, P. W., Nolan, J. M., Cialdini, R. B., Goldstein, N. J., & Griskevicius, V. (2007). The constructive, destructive, and reconstructive power of social norms. Psychological Science, 18(5), 429–434.",
    kind: "期刊",
    status: "已核（PMID 17576283）",
    link: "https://doi.org/10.1111/j.1467-9280.2007.01917.x",
  },
];

export const citationRules = [
  "一手优先：能引原文的不引转述。",
  "维基类页面只作线索、不作引用。",
  "英文文献给原文＋中文译名，页面只显示中文。",
];

export type Observation = {
  n: string;
  title: string;
  detail: string;
  link: string;
  tag: string;
};

export const observations: Observation[] = [
  {
    n: "①",
    title: "公约贴了两处，我一条也说不出来。",
    detail:
      "居民公约贴在物业楼下和每栋楼的电梯旁。可问我自己写了什么，我答不上来。这不是记性差——命令性规则要生效靠社会评价，而一份只负责张贴的公约，身边没有评价它的人，它剩下的功能只有两个：一份没人读的文本，和出事以后追责的依据。",
    link: "接回教材：命令性规则与社会评价绑定（p.145）",
    tag: "命令性规则",
  },
  {
    n: "②",
    title: "监督撤了，互助网留下了。",
    detail:
      "疫情期间小区出现过团购群、志愿者、消杀和卡口值班。疫情后，消杀和卡口值班消失了，团购群留到今天。撤掉的是外部监督，留下的是还有来回的互助网。",
    link: "接回教材：长期的重复性博弈减少了（p.138）；互惠原则促进友善行为（p.147）",
    tag: "重复性博弈",
  },
  {
    n: "③",
    title: "养狗、停车、装修的冲突，最后都是物业出面。",
    detail: "不是我，不是邻居，也不是楼长——是物业。熟人社区靠邻里舆论，陌生人社区靠第三方规则来执行。",
    link: "接回教材：左邻右舍都是陌生人（p.138）",
    tag: "第三方执行",
  },
];

export const observationCaveat =
  "个人观察 ｜ 两个小区：2005–2015 年旧小区、2015 年至今新小区，均为居民楼公寓；样本两名小区、一名汇报人，不构成研究证据，只用于说明机制。";

export const method = {
  title: "方法",
  text: "每条主张都先落到教材的具体页码，再考虑是否外延；外延材料（乡约、法条、英文文献）一律放附录，正文只在第 2 页留一行。",
};

export const limits = {
  title: "限制",
  text: "一手材料是个人观察（两个小区、一名汇报人），只用于说明机制，不用于证明「文明在退步」；中西比较与历史材料取自教材与公开文献，未经独立考证的部分已标注；三个小节标题已按扫描件核出（第一节 文明观概述／第二节 社区文明观的特性与研究主题／第三节 文明社区建设），页码与措辞仍待教材实物抽验。",
};

export const divergence = {
  title: "与一份流传较广的整理稿的差异",
  text: "另有整理稿把这一章讲成「五德、四维（公共意识／规则意识／公德行为／社区认同）、居民公约、垃圾分类、文明养犬」。核对原书后发现框架不同：原书这一章的骨架是「文明观概述 → 社区文明观的特性与研究主题 → 文明社区建设」。逐词检索全章：「居民公约」0 次、「社会主义核心价值观」0 次、「垃圾分类」1 次、「社区公约」1 次、「五德」0 次。本汇报一律以教材原文为准，整理稿只作参考，不进正文。",
};

export const pageIndex = [
  { page: "P1 一个苹果", ref: "p.124" },
  { page: "P2 本章地图", ref: "p.124–125、129–131" },
  { page: "P3 这本书的底子", ref: "p.128–129" },
  { page: "P4 三个矛盾", ref: "p.137–138、140–141" },
  { page: "P5 看得见的环境", ref: "p.140、144–145" },
  { page: "P6 看得见的别人", ref: "p.145–146" },
  { page: "P7 看得见的将来", ref: "p.142–144" },
  { page: "P9 结论", ref: "p.130、138、141、148" },
];
