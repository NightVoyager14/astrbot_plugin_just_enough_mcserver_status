
<div align="left">
    <img src="https://cdn.jsdelivr.net/gh/NightVoyager14/astrbot_plugin_just_enough_mcserver_status@main/logo.png" width="120"/>
    <h1>Just Enough McServer Status</h1>
</div>

[![License](https://img.shields.io/badge/License-AGPL_v3-orange.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![repo](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status)
[![Python](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![version](https://img.shields.io/github/v/tag/NightVoyager14/astrbot_plugin_just_enough_mcserver_status?label=JEMSS)](https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/releases/latest)
[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-skyblue)](https://github.com/AstrBotDevs/AstrBot)

> 一个为AstrBot实现Minecraft服务器查询功能的插件，图片渲染本地化，无需额外浏览器环境

## 写在前面

本插件处于*开发中（InDev）*，核心功能可用，但尚不完善  
如果你有遇到BUG或者有功能建议，欢迎提 [Issue](https://github.com/NightVoyager14/astrbot_plugin_just_enough_mcserver_status/issues) 反馈！

## 效果展示

![example01](https://cdn.jsdelivr.net/gh/NightVoyager14/astrbot_plugin_just_enough_mcserver_status@main/images/example01.png)

## 插件功能

### 指令

- **`/jeping status <服务器地址[:端口]> [名称]`** — 获取 Java 版服务器状态（在线人数、MOTD、延迟等）
- **`/jeping status`** — 快捷获取预设服务器信息
- **`/jemss version`** — 查看插件版本
- **`/jemss splash`** — 随机获取一条启动标语
- **`/jemss admin`** (管理员) — 管理员测试指令
- **`/jemss help`** — 显示帮助信息

### Agent tools

- `je_server_status` — 为AI提供查询接口

## 插件配置

> [!NOTE]
> v1.1.0更新完全抛弃了旧版本 `config.toml` 的配置方式，而转向了AstrBot框架提供的配置管理接口  
> 这意味着旧版本的配置在更新后会失效，且旧配置文件会被完全删除

插件在 *未来* 计划开放更多可自定义选项  
目前插件可于AstrBotUI中配置，已完成一些基础配置项的实现  
  
配置项目前包含：

- **通用**
  - 信息卡片渲染
  - 文字信息输出
- **快捷查询**
  - 预设服务器
- **文字信息**
  - Markdown格式输出
- **信息卡片**
  - 延迟指示器
    - 阈值
  - 图标
  - 标题
  - MOTD
    - 行间距
  - 在线人数
  - 背景
    - 自定义背景
    - 上传背景图片

## 特别感谢

- [mctext](https://github.com/Hexze/mctext) 提供的Minecraft字体文件  
- [mcstatus](https://github.com/py-mine/mcstatus) 提供的Minecraft服务器查询与数据解析实现  
- [AstrBot](https://github.com/AstrBotDevs/AstrBot) 提供的优秀机器人框架  

## 附录

- [错误码查询手册](docs/ERROR_CODES.md)

<div align="center">
<img src="https://cdn.jsdelivr.net/gh/NightVoyager14/astrbot_plugin_just_enough_mcserver_status@main/images/watashiwa-koseino-desukara.gif" width="100"/>

私は、高性能ですから！Minecraftの対応も、もちろんお手の物です！
</div>

---

**Disclaimer:** This project is **NOT AN OFFICIAL MINECRAFT PRODUCT**. It is **NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT**.
