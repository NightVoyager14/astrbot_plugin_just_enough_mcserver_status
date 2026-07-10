# Changelog

## [v1.1.0] - 2026-07-10

### Breaking changes

- 更换了配置文件管理系统，现使用AstrBot框架提供的Config管理接口
- 删除了原来的配置文件 `config.toml`

### Added

- 简单添加了信息卡片的各个元素的配置项
- 用Markdown美化文本输出格式
- 添加错误码文档
- 添加了依赖项 `pydantic`

### Changed

- 将README图片链接从Github迁移到jsDelivr，以避免Github的速率限制和加速图片渲染
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

[v1.1.0]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.1.0
[v1.0.1]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.0.0
[v1.0.0]: https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/tree/v1.0.0
