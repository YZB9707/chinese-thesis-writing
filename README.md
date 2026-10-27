# 中文本科毕业论文写作 Skill

一个给 AI agent 用的中文论文写作规范：怎么把中文写得不像机器生成、怎么按学院表格模板套版、怎么处理文献与数字、交稿前查什么。

适用于中文本科毕业论文的开题报告与正文写作。不适用于硕士、博士学位论文的评审标准。

## 安装

**Hermes**

```bash
hermes skills install YZB9707/chinese-thesis-writing/chinese-thesis-writing
```

**Claude Code**

```bash
git clone https://github.com/YZB9707/chinese-thesis-writing.git
cp -r chinese-thesis-writing ~/.claude/skills/
```

只认用户级的 `~/.claude/skills/<name>/SKILL.md`，项目级的 `.claude/skills/` 不生效（实测）。

**其他 agent**

把 `SKILL.md` 当作 instructions 文件喂进去，`references/` 放在旁边目录，保持相对路径。

装完请开新会话，技能才进索引。

## 里面有什么

| 文件 | 内容 | 什么时候读 |
|---|---|---|
| `SKILL.md` | 触发条件、路由表、15 条铁律、8 步流程 | 每次都读 |
| `references/ai-tone-rules.md` | 去 AI 味四层规则、段落层、错落、三次实测（47% / 0% / 24%） | 动笔前、判红时 |
| `references/template-cloning.md` | 表格型开题报告的克隆步骤与六个小节 | 写开题时 |
| `references/structure-and-format.md` | 无第一人称、论述句、部件顺序、版面参数 | 审格式时 |
| `references/literature-and-data.md` | 题录照抄、GB/T 7714、派生数字重算、不编数据 | 写文献时 |
| `references/wording-and-anonymity.md` | 措辞留余地、校名与人名的匿名处理 | 拿到真名真校时 |
| `references/delivery-checklist.md` | 交稿清单、docx 页数表数核对 | 交稿前 |
| `scripts/rule_audit.py` | 硬伤自检：句长标准差、段长、对仗、第一人称、破折号 | 写完一稿、交稿前 |

`SKILL.md` 里有一张路由表，按用户的原话决定读哪一份。没有这张表，`references/` 装了也不会被读。

## 跑自检

```bash
python scripts/rule_audit.py 论文.docx
```

输出句长标准差、超过 25 字长句占比、段长分布、段内句数极差、对仗密度和超长句坐标。退出码 1 表示有硬伤。

## 它不会做什么

- 不生产数据：拿不到的数写“未取得”，不编。
- 不承诺检测结果：只管句式与形状，分数由检测器说了算。
- 不代写真实学校的实名稿：校名可换真名，教师与学生一律不写姓名。

## 原始手册

`docs/中文本科毕业论文写作-Skill与记忆.docx` 是这套规则的手册版（15 页、10 个表、近万字），带实测数据与改前改后原文。给 agent 用的是上面的 markdown，给人读的是这份 docx。

## 许可

MIT。见 `LICENSE`。
