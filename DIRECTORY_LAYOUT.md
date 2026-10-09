# 目录结构 / Directory layout

[首页 / Home](README.md) · [文档索引 / Documentation](docs/README.md)

按使用目的组织入口：首页看功能与下载，型号页核对适配范围，复现指南连接代码与证据，研究历程解释每次修改。

Entry points follow the reader's task: features and downloads, model scope, reproduction, then research and evidence.

```text
README.md / README.en.md    中文 / English landing pages
CHANGELOG.md               Revision summary, distinct from the full history
CONTRIBUTING.md            Issue and contribution requirements
.github/                   Bug report, feature request and PR templates
docs/
  README.md                Documentation index
  devices/                 V100F / V480F model pages and catalog.json
  DOWNLOADS.md             Release BINs, hashes and manifests
  REPRODUCE.md             Shared entry point for both model-specific tools
  HARDWARE_STATUS.*        Deployment reports and acceptance scope
  PROJECT_HISTORY*.md     Detailed bilingual development history
  native/                  Format, architecture, validation, recovery, SU-1 TTL
  debugger/                Desktop workbench guides
  releases/                Published release notes
  REFERENCES.md            External references and scope of inspiration
native/                    V100F R7 implementation
  src/ patches/ metadata/  Source, exact patches and hook records
  lab/ tests/ evidence/    Bounded execution, patcher tests and saved results
  patcher.py build.py      Exact-version patching and source reproduction
v480/                      V480F v2 implementation, same internal grouping
debug/ tests/              Desktop parameter workbench and its tests
scripts/                   Repository documentation/catalog validation
firmware/                  Locally supplied original inputs, ignored by Git
```

V100 的源码目录继续使用 `native/`，V480 使用 `v480/`，保留既有构建命令和证据中的路径。统一的 `docs/devices/` 入口给两款灯相同的信息结构。两个实现各自拥有 `src / patches / metadata / lab / tests / evidence`，不因框架相似而混用偏移。

V100 source retains `native/` and V480 retains `v480/` so existing commands and evidence paths continue to work. `docs/devices/` provides a consistent model index. Each implementation owns its source, patches, metadata, execution checks, tests and evidence; offsets are not shared by assumption.

BIN 放在 GitHub Releases，源码与补丁清单放在 Git；原厂输入、输出缓存和私人调试会话不进入版本控制。源码树的组织调整不改变已发布 BIN。

BINs live in GitHub Releases; source and patch records live in Git. Official inputs, build caches and private sessions stay local. Documentation organization does not change the released images.
