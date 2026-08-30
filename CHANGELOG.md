# Changelog

## [v1.2.0] - 2026-08-30

### Added

- **添加了基岩版查询的指令 `/beping status`**
- **添加了基岩版查询的 Agent Tool `mcbe_server_status`**
- **添加新的基岩版信息卡片主题**
- 添加了快捷查询的默认查询功能
- 添加了信息卡片的时间戳水印

### Changed

- 优化项目结构，将源码移入 src 中
- 初步尝试添加 config 解析测试
- 优化 README 版本展示与文档结构

### Fixed

- 修复了快捷查询的配置检验中 template_key 无法匹配而导致检验失败的问题
- 修复了 `help` 指令中新指令支持信息不全面问题
- 修复 README 中错误的指令介绍

**Diff**: <https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/compare/v1.1.1...v1.2.0>

## [v1.1.1] - 2026-08-02

### Added

- 添加多个配置项：图片输出与文字输出显示，MOTD行间距，快捷查询服务器预设
- 增加了快捷查询功能
- 添加了对 WebColor 以及渐变色渲染的支持

### Changed

- 统一并优化配置项函数及变量命名

### Fixed

- 修复由于 ForgeDataChannel 对象无法转换成 json 格式导致 Agent Tool 查询失败的问题

**Diff**: <https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/compare/v1.1.0...v1.1.1>

## [v1.1.0] - 2026-07-10

### Breaking Changes

- 更换了配置文件管理系统，现使用 AstrBot 框架提供的 Config 管理接口
- 删除了原来的配置文件 `config.toml`

### Added

- 简单添加了信息卡片的各个元素的配置项
- 用 Markdown 美化文本输出格式
- 添加错误码文档
- 添加了依赖项 `pydantic`

### Changed

- 将 README 图片链接从 Github 迁移到 jsDelivr ，以避免 Github 的速率限制和加速图片渲染
- 重新设计异常处理，使排查错误更加清晰
- 添加新增配置项的介绍

### Removed

- 删除了依赖项 `tomlkit`

**Diff**: <https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/compare/v1.0.1...v1.1.0>

## [v1.0.1] - 2026-07-04

### Fixed

- 修复了在 AstrBot UI 中插件文档图片无法正常加载的问题

### Changed

- 优化了插件命令和 Agent Tool 输出
- 将 MOTD 渲染及状态图绘制逻辑抽离为独立模块 `Renderer`，提升代码可维护性。

**Diff**: <https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/compare/v1.0.0...v1.0.1>

## [v1.0.0] - 2026-06-27

这里是JEMSS的首个Release，虽然说这个插件目前还很不完整，只有部分核心功得以实现。
不过我认为其已经到了可以使用的最低限度，于是便决定发布了v1.0.0版本。

### 已实现功能

- Java Edition 服务器信息查询指令
- Java Edition 服务器查询Agent Tool
- Java Edition 服务器查询信息原版风格图片展示
- Java Edition Splashes随机抽取

[v1.2.0]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.2.0
[v1.1.1]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.1.1
[v1.1.0]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.1.0
[v1.0.1]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.0.1
[v1.0.0]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.0.0
