RedDust object-only runtime asset pack v33
用途：游戏运行时直接使用的透明 PNG 素材。

本版修正：
- 解决 v30 过度清理造成的人物、扇叶和小尺寸素材主体损坏。
- 人物/事件/UI/fan rotor 使用完整源图恢复主体。
- 食品盒、凳子、工具箱等容易带地垫的道具沿用 v30 的干净 object-only 主图。
- 64/128/512 小图全部从最终主图重新缩放，避免小尺寸图被切坏。
- 透明区域 RGB 已固色，减少缩放合成时出现白/绿边。

目录：
- assets/: 按 characters/resources/props/scenes/events/ui 分类的运行时 PNG。
- previews/: 主体完整性和场景合成检查图。
- metadata/: 修复报告。
- asset-name-map-cn.csv / asset-name-map-cn.md: 中文名称与文件名对照。
