# SHELTER · AI 生图 Prompt 全集

> 工具：Midjourney v6 / Stable Diffusion XL / DALL-E 3（均可使用）
> 版本：v1.0 · 2026-05-10
> 对应素材清单：[asset-procurement.md](asset-procurement.md)

---

## 使用说明

**每条 prompt 直接粘贴到 Midjourney `/imagine` 或 SD 提示词框。**

Midjourney 追加参数建议：
- 角色 sprite：`--ar 3:4 --style raw --v 6`
- 场景背景：`--ar 16:9 --style raw --v 6`
- 图标/道具：`--ar 1:1 --style raw --v 6`
- 生成多变体后用 `/vary (subtle)` 保留风格稳定性

**固定风格 DNA（每条 prompt 末尾默认包含）：**

> `hand-drawn cartoon illustration, 60 Seconds! Reatomized game art style, exaggerated cartoon proportions, slightly grotesque warmth, muted desaturated warm color palette (browns oranges), WALL-E inspired cute worn robots, post-apocalyptic electromagnetic storm world, 2D game art, NOT cyberpunk NOT neon glow NOT realistic`

下文每条 prompt 已内嵌此风格 DNA，无需重复添加。

---

## ─── P0 优先 ─── （7天Demo必须）

---

## 一、场景资源

### SC-01 · 避难所室内（基础）

```
underground shelter interior, arched concrete bunker room, dim warm industrial lighting from ceiling lamp, metal shelving unit with supplies, old CRT monitor on desk, charging dock in corner, heavy blast door on left wall, security camera screen showing outside, worn wooden floor, cozy but claustrophobic atmosphere, side-view 2D game background, layered composition with clear foreground/midground/background, hand-drawn cartoon illustration, 60 Seconds! Reatomized game art style, muted warm browns #3a2820, orange lamp glow, no robots in scene just environment, clean linework with painterly fill --ar 16:9 --style raw --v 6
```

### SC-03 · 避难所外景（窗外/监控画面）

```
post-apocalyptic industrial cityscape seen through security camera, collapsed factory buildings silhouette, blue electrical arcs crackling in purple hazy sky, electromagnetic storm atmosphere, distant city ruins, desaturated cool tones contrasting with warm shelter interior, grainy black-and-white surveillance footage style with slight color bleed, hand-drawn cartoon illustration style, 60 Seconds! Reatomized art direction, slightly grotesque industrial wasteland --ar 16:9 --style raw --v 6
```

### SC-05 · 远景城市轮廓

```
distant destroyed city skyline silhouette, crumbling industrial buildings, electromagnetic storm clouds above, blue lightning arcs between ruined towers, purple-grey sky atmosphere, minimal detail suitable for background layer, 2D game parallax background layer, hand-drawn cartoon illustration, muted desaturated palette, slightly ominous but not horror --ar 16:9 --style raw --v 6
```

---

## 二、家具与物件

### FN-01 · 充电座（Charging Station）

```
robot charging dock station, industrial design, glowing blue charge indicator light, metal frame with power cables, slightly worn and scratched, cozy nook feel, side view, 2D game asset, white background, hand-drawn cartoon illustration, 60 Seconds! Reatomized style, warm muted tones, pixel art inspired flat shading --ar 1:1 --style raw --v 6
```

### FN-02 · 主控终端（CRT Terminal）

```
old CRT computer terminal with keyboard, green phosphor screen glow, chunky retro design, worn industrial look, Fallout-inspired bunker computer, cables running out back, side view 2D game asset, white background, hand-drawn cartoon illustration, warm browns and green screen glow, slightly grotesque retro charm --ar 1:1 --style raw --v 6
```

### FN-03 · 储物机柜（Supply Cabinet）— 3帧

```
[满载版] metal industrial storage cabinet shelves, fully stocked with cylindrical batteries and blue coolant bottles, warm brown metal, slightly dented, 2D game asset side view, white background, hand-drawn cartoon illustration style --ar 1:1 --style raw --v 6

[半空版] same metal storage cabinet, half empty shelves, a few batteries remaining, visible empty shelf space, slightly more worn look --ar 1:1 --style raw --v 6

[空载版] empty metal storage cabinet, bare shelves, dust marks where items used to be, sad and bare atmosphere --ar 1:1 --style raw --v 6
```

### FN-04 · 收音机（Vacuum Tube Radio）

```
vintage vacuum tube radio, Fallout-inspired chunky design, glowing orange signal light, analog dials and knobs, worn bakelite casing with scratches, warm amber tube glow, side view 2D game asset, white background, hand-drawn cartoon illustration, retro post-apocalyptic aesthetic --ar 1:1 --style raw --v 6
```

### FN-05 · 应急照明灯 — 2帧

```
[亮] industrial emergency work lamp, warm yellow-orange light cone, heavy metal casing, adjustable arm, switched on with visible light halo effect, 2D game asset, white background, hand-drawn cartoon style --ar 1:1 --style raw --v 6

[暗] same industrial lamp switched off, cold grey metal, no light, slightly ominous --ar 1:1 --style raw --v 6
```

### FN-06 · 屏蔽闸门（Blast Door）— 4帧

```
[关闭] heavy electromagnetic shielded blast door, thick metal with large rivets and bolts, industrial warning stripes, sealed shut, imposing and secure, 2D game asset front view, hand-drawn cartoon illustration, muted grey-brown industrial palette --ar 2:3 --style raw --v 6

[半开] same blast door 30% open, hydraulic pistons visible, dramatic lighting from gap --ar 2:3 --style raw --v 6

[敲门震动] same door with motion blur/vibration lines around it, dust particles falling, someone knocking --ar 2:3 --style raw --v 6

[完全开启] blast door fully open, hydraulic pistons extended, dramatic corridor beyond --ar 2:3 --style raw --v 6
```

### FN-07 · 监控屏幕

```
old CRT security monitor showing grainy black-and-white exterior camera footage, slight scan lines, electromagnetic interference static at edges, chunky monitor casing, mounted on wall bracket, 2D game asset, hand-drawn cartoon illustration, muted tones --ar 4:3 --style raw --v 6
```

---

## 三、资源道具图标

> 以下所有道具：白背景、正面视角、适合32×32或64×64像素图标用途

### RS-01 · 电池 🔋 — 3帧

```
[满电] single cylindrical battery, green charge indicator ring, clean industrial design, slightly worn label, soft glow, 2D game item icon, white background, hand-drawn cartoon illustration, warm muted tones, NOT cyberpunk --ar 1:1 --style raw --v 6

[半电] same cylindrical battery with yellow indicator ring, slightly depleted look --ar 1:1 --style raw --v 6

[低电] same battery with red blinking indicator, cracked casing, desperate energy --ar 1:1 --style raw --v 6
```

### RS-02 · 冷却液 ❄️ — 2帧

```
[满] blue liquid coolant bottle, translucent with visible blue fluid inside, industrial label, metal screw cap, 2D game icon, white background, hand-drawn cartoon style, cool blue accent on warm background --ar 1:1 --style raw --v 6

[空] same bottle empty, faint blue residue inside, slightly crushed and dusty --ar 1:1 --style raw --v 6
```

### RS-03 · 修理包 🔧

```
industrial repair kit toolbox, red cross symbol on lid, worn metal case with latches, slightly dented, tools peeking out edge, 2D game item icon, white background, hand-drawn cartoon illustration style, warm muted palette with red cross accent --ar 1:1 --style raw --v 6
```

### RS-04 · 工具（3件）

```
[扳手] heavy adjustable wrench, worn chrome finish with rust spots, 2D game item icon, white background, hand-drawn cartoon style --ar 1:1 --style raw --v 6

[螺丝刀] flathead screwdriver with worn wooden handle, industrial look --ar 1:1 --style raw --v 6

[焊枪] welding torch with small flame tip, industrial design, slightly scorched --ar 1:1 --style raw --v 6
```

### RS-05 · 脉冲枪 ⚡

```
electromagnetic pulse pistol, modified industrial tool converted to weapon, exposed copper coil winding, blue electrical accent, chunky handmade look, riveted metal housing, 2D game item icon, white background, hand-drawn cartoon illustration, NOT sleek NOT cyberpunk, more DIY wasteland feel --ar 1:1 --style raw --v 6
```

### RS-07 · 数据磁盘 💾 — 3种

```
[标准] vintage 3.5" floppy disk, hand-written label sticker, slightly worn edges, 2D game icon --ar 1:1 --style raw --v 6

[重要] floppy disk with red warning label, urgent marking --ar 1:1 --style raw --v 6

[损坏] floppy disk with cracked casing, scratched surface --ar 1:1 --style raw --v 6
```

### RS-08 · 扑克牌 🃏

```
worn playing card deck in tattered box, dog-eared corners, familiar but weathered, 2D game icon, white background, hand-drawn cartoon illustration, warm aged tones --ar 1:1 --style raw --v 6
```

---

## 四、角色 — Hero 机器人

> **角色生成策略**：先生成「待机 (idle)」帧确定外观设计，通过 img2img 或 Vary 保持一致性，再生成其他7个状态帧。

### 通用角色 prompt 框架

```
[角色描述], cute worn cartoon robot character, exaggerated proportions (large square head, small body, visible joints), LED screen face displaying [表情], slightly weathered and scratched surface, full body front view, 2D game character sprite, white background, hand-drawn cartoon illustration, 60 Seconds! Reatomized character art style, WALL-E inspired warmth, muted [主色] palette with [辅色] accents, NOT cyberpunk NOT realistic
```

### 状态帧表情对照

| 状态 | LED 屏幕表情 | 身体姿势 |
|---|---|---|
| 待机 (idle) | ●● 圆点眼 | 站立放松，轻微晃动 |
| 行走 (walk) | ●● | 迈步，手臂摆动 |
| 充电 (charging) | zzz 或充电图标 | 坐在充电座，眼睛半闭 |
| 修理 (repair) | 🔧 工具图标 | 弯腰检查，手持工具 |
| 思考 (thinking) | ◐ 加载旋转 | 手托头部，歪头 |
| 受伤 (damaged) | X X 红叉 | 跌倒姿势，火花从身体喷出 |
| 庆祝 (celebrate) | ^_^ 笑脸 | 双手举起，跳跃 |
| 报废 (offline) | ■ 黑屏 | 倒在地上，烟雾 |

---

### AG-01 · R-01 守望者 (Guardian) — P0

**外观**：大块头军用造型，方正护甲板，灰绿色，红色警告灯

```
[待机] bulky military-grade guardian robot, heavy square armor plating, broad shoulders, thick legs, army green-grey color scheme with red warning indicator lights on chest, square LED face screen showing calm dot eyes (●●), industrial riveted armor, slightly battle-worn, full body front view, 2D game character sprite, white background, hand-drawn cartoon illustration, 60 Seconds! game art style, WALL-E inspired cute-tough balance, exaggerated cartoon proportions --ar 3:4 --style raw --v 6

[思考] same guardian robot R-01, loading spinner on LED face screen (◐), hand raised to chin in thinking pose, armor plates same grey-green with red lights, full body, white background --ar 3:4 --style raw --v 6

[受伤] same guardian robot R-01, X X on LED face, tilted damaged stance, orange sparks bursting from left shoulder joint, crack in chest armor plate, smoke wisps --ar 3:4 --style raw --v 6

[报废] same guardian robot R-01, fallen backwards, LED screen black (■), battle-damage cracks across armor, faint smoke rising, still and silent --ar 3:4 --style raw --v 6
```

---

### AG-02 · R-02 速行者 (Runner) — P0

**外观**：流线型快递机器人，轻巧，黄黑配色（DHL风）

```
[待机] slim speedy delivery robot, streamlined aerodynamic body, lightweight frame with thin legs, yellow and black color scheme with delivery company styling, small LED screen face with alert dot eyes, carrying strap or delivery pouch detail, fast-looking posture even while standing, full body front view, 2D game character sprite, white background, hand-drawn cartoon illustration, 60 Seconds! game art style, WALL-E warmth, exaggerated proportions --ar 3:4 --style raw --v 6

[行走] same runner robot R-02, mid-stride action pose, one leg up, arms back in running motion, yellow-black color consistent, LED eyes focused forward --ar 3:4 --style raw --v 6

[思考] same runner robot R-02, stopped mid-motion, loading spinner LED face, one hand raised as if checking data --ar 3:4 --style raw --v 6

[受伤] same runner robot R-02, stumbled pose, one knee down, X X LED face, sparks from ankle joint --ar 3:4 --style raw --v 6
```

---

### AG-03 · R-03 织梦者 (Dreamer) — P0 · **Demo 主角，优先完成全8帧**

**外观**：高瘦实验室造型，单镜头眼睛，白色主体+蓝色光环

```
[待机] tall slender laboratory researcher robot, elegant proportions, single large camera lens eye on smooth white face plate, slim white chassis with soft blue LED ring around neck/collar, delicate articulated fingers, scientist-like posture, calm and thoughtful demeanor, full body front view, 2D game character sprite, white background, hand-drawn cartoon illustration, 60 Seconds! game art style, WALL-E quiet dignity, white and pale blue color scheme, slightly worn lab-coat-inspired chassis design --ar 3:4 --style raw --v 6

[行走] same dreamer robot R-03, graceful walking pose, white chassis, blue LED ring, single lens eye, arms slightly swinging, thoughtful stride --ar 3:4 --style raw --v 6

[充电] same dreamer robot R-03 seated at charging dock, single lens eye dimmed to half (sleep mode), blue charging glow around connection point, peaceful resting pose --ar 3:4 --style raw --v 6

[修理] same dreamer robot R-03 leaning forward examining something, single lens eye zoomed in (pupil contracted), holding small diagnostic tool, focused and careful --ar 3:4 --style raw --v 6

[思考] same dreamer robot R-03, hand touching chin area, single lens eye showing circular loading indicator, slight head tilt, deeply contemplative --ar 3:4 --style raw --v 6

[受伤] same dreamer robot R-03, staggered backwards, single lens eye cracked with spider crack, X displayed on crack, orange sparks from right shoulder, white chassis dented --ar 3:4 --style raw --v 6

[庆祝] same dreamer robot R-03, arms raised overhead, single lens eye displaying happy expression ^^, blue LED ring pulsing bright, jumping slightly --ar 3:4 --style raw --v 6

[报废] same dreamer robot R-03 collapsed forward, single lens eye dark and shattered, white chassis cracked and scorched, smoke rising, OFF displayed faintly --ar 3:4 --style raw --v 6
```

---

### AG-04 · R-04 断锋 (Breaker) — P0

**外观**：棱角分明，安保改装，暗红+黑

```
[待机] angular security-modified robot, sharp geometric armor plating, intimidating stance even at rest, dark crimson red and black color scheme, LED face showing narrow stern eyes (--), reinforced shoulder guards, visible weapon mount points (empty), full body front view, 2D game character sprite, white background, hand-drawn cartoon illustration, 60 Seconds! game art style, tough but still cartoon cute in proportions --ar 3:4 --style raw --v 6

[思考] same breaker robot R-04 dark red-black, narrow LED eyes shifting to loading symbol, arms crossed, calculating stance --ar 3:4 --style raw --v 6

[受伤] same breaker robot R-04, armor plate cracked, dark energy sparks, X X LED face, still standing but damaged --ar 3:4 --style raw --v 6

[庆祝] same breaker robot R-04, rare moment of joy, LED face showing surprised happy expression, one fist raised, looks slightly awkward celebrating --ar 3:4 --style raw --v 6
```

---

### AG-05 · R-05 和声 (Harmony) — P1

**外观**：圆润友好客服造型，米白+暖橙

```
[待机] round friendly customer service robot, soft rounded body with no sharp edges, warm cream white color with orange accent details, cheerful LED face smile (‿), open welcoming arm position, slightly chubby proportions conveying warmth, full body front view, 2D game sprite, white background, hand-drawn cartoon illustration --ar 3:4 --style raw --v 6
```

---

### AG-06 · R-06 精算 (Calculator) — P1

**外观**：整洁西装感，办公型，灰蓝+银

```
[待机] office accountant robot, neat and tidy design with suit-like panel detailing, grey-blue and silver color scheme, rectangular LED screen face displaying focused eyes with reading glasses visual indicator, holding clipboard or data device, posture upright and professional, full body front view, 2D game sprite, white background, hand-drawn cartoon style --ar 3:4 --style raw --v 6
```

---

### AG-07 · R-07 引路 (Pathfinder) — P1

**外观**：装备很多，探险型，橙色+棕

```
[待机] heavily equipped explorer robot, covered in attached gadgets tools and pouches, adventurous orange and brown color scheme, LED face showing eager eyes, multiple carried tools (compass, rope, sensor), stocky adventure-ready build, full body front view, 2D game sprite, white background, hand-drawn cartoon style --ar 3:4 --style raw --v 6
```

---

### AG-08 · R-08 扣板机 (Dealer) — P2

**外观**：花哨赌场荷官，黑金+紫

```
[待机] flashy casino dealer robot, ornate decorative chassis with card suit motifs, black and gold color scheme with subtle purple accent, LED face showing suave confident expression (◡), holding playing cards, jaunty tilted hat attachment, full body front view, 2D game sprite, white background, hand-drawn cartoon style --ar 3:4 --style raw --v 6
```

---

## 五、NPC 机器人

### NP-01 · 老家政机器人 — P0 · **情感锚点，重点打磨**

```
[站立] small squat ball-headed domestic service robot, rounded spherical head with single large camera lens eye, short stocky body, rusty and weathered patina, original service company logo faded on chest, kind and worn appearance, full body front view, 2D game sprite, white background, hand-drawn cartoon illustration, 60 Seconds! NPC style, WALL-E aged robot warmth --ar 3:4 --style raw --v 6

[敲门] same old housekeeper robot, fist raised knocking motion, slightly hunched over, single lens eye looking hopeful and tired, front view --ar 3:4 --style raw --v 6

[微笑] same old housekeeper robot, LED face or camera lens displaying warm smile expression ^_^, slight lean forward in friendly greeting --ar 3:4 --style raw --v 6
```

---

### NP-02 · 抱孩子的母机 — P0

```
[站立] damaged mother robot holding small baby robot in arms, one arm damaged and hanging limp with exposed wiring, protective maternal posture, baby robot is tiny simple design nestled against chest, weathered and battle-worn but nurturing, full body front view, 2D game sprite, white background, hand-drawn cartoon illustration, emotionally resonant, NOT horror --ar 3:4 --style raw --v 6

[递孩子] same mother robot extending damaged arms forward offering the baby robot, pleading LED expression on face --ar 3:4 --style raw --v 6
```

---

### NP-03 · 神秘陌生人 — P0

```
[站立] mysterious unknown robot, completely matte black chassis with no markings or identifiers, featureless smooth face plate (no LED screen visible), slightly taller than average, unnervingly still posture, faint outline visible, full body front view, 2D game sprite, white background, creates tension through absence of detail, hand-drawn cartoon illustration, 60 Seconds! style --ar 3:4 --style raw --v 6

[转身] same mysterious black robot, mid-turn pose showing back, even back has no markings, unsettling anonymity --ar 3:4 --style raw --v 6
```

---

### NP-04 · 拾荒者老锈 (Scavenger) — P0

```
[站立] dangerous scavenger robot, industrial worker type with improvised self-welded armor plates bolted over original chassis, mismatched metal pieces, carrying steel pipe weapon, orange rust patches across grey body, menacing but still cartoonishly exaggerated, full body front view, 2D game sprite, white background, hand-drawn cartoon style, 60 Seconds! NPC energy --ar 3:4 --style raw --v 6

[挥武器] same scavenger robot, steel pipe raised threateningly, aggressive attack pose, rust and sparks --ar 3:4 --style raw --v 6

[抢东西] same scavenger robot, grabbing motion with one arm, greedy hunched posture --ar 3:4 --style raw --v 6
```

---

### NP-05 · 拾荒者三人组 — P1

```
[撬棍专家] lean scavenger robot specialized in breaking entry, carrying large crowbar, wiry agile build, mismatched salvaged parts --ar 3:4 --style raw --v 6

[武力型] heavy scavenger robot, bulky improvised armor, fists raised, intimidating size, rust and dents --ar 3:4 --style raw --v 6

[扫描型] sneaky scavenger robot, scanner sensor array on head, crouching spy posture, information-gathering specialist --ar 3:4 --style raw --v 6
```

---

### NP-06 · 旧货郎商人 — P1

```
[站立] merchant robot with wheeled cart full of salvaged goods hanging and stacked, cheerful salesperson expression, many pockets and pouches, items dangling from cart (tools, batteries, parts), 2D game sprite, white background, cartoon style --ar 3:4 --style raw --v 6
```

---

### NP-07 · 流浪 R 系列（受伤同类）— P1

```
[站立] damaged wandering robot of same series as heroes, one leg replaced with crude wooden crutch, battle-scarred chassis, worn and tired LED expression, surviving against odds, full body, 2D sprite, white background --ar 3:4 --style raw --v 6
```

---

### NP-08 · 小 7（流浪儿童机器人）— P1

```
[站立] small child-sized robot, one eye camera lens broken and dark, other eye bright and curious, tiny proportions, innocent and vulnerable, childlike posture, 2D sprite, white background, emotionally compelling, hand-drawn cartoon style --ar 3:4 --style raw --v 6

[哭] same child robot small-7, liquid (oil?) dripping from working eye, downturned LED expression, arms wrapped around self --ar 3:4 --style raw --v 6
```

---

### NP-09 · 救援队伊尔达 — P1

```
[站立] large military rescue robot, official government authority look, heavy shielded chassis with government organization insignia, shield carried in one arm, represents hope and order, imposing but reassuring, full body, 2D sprite, white background --ar 3:4 --style raw --v 6
```

---

## 六、UI 元素

> UI 元素建议用 Midjourney 生成后在 Figma/Photoshop 中修改适配，或直接用 SVG 手工制作。

### UI-01 · 资源图标组（8个）

```
[电池图标] single battery icon, cylindrical with green charge indicator, clean simple design suitable for game UI, flat 2D icon style, transparent background or white background, industrial aesthetic, 64x64 resolution hint --ar 1:1 --style raw --v 6

[冷却液图标] coolant bottle icon, blue translucent liquid visible, simple flat 2D game UI icon style --ar 1:1 --style raw --v 6

[修理包图标] repair kit toolbox icon, red cross detail, simple flat 2D game UI --ar 1:1 --style raw --v 6

[工具图标] wrench and screwdriver crossed icon, simple industrial flat 2D game UI --ar 1:1 --style raw --v 6

[脉冲枪图标] EMP pulse pistol icon, blue electrical coil detail, simple flat 2D game UI --ar 1:1 --style raw --v 6

[收音机图标] vintage vacuum tube radio icon, warm orange glow, simple flat 2D game UI --ar 1:1 --style raw --v 6

[磁盘图标] floppy disk icon, 3.5 inch format, simple flat 2D game UI --ar 1:1 --style raw --v 6

[扑克图标] playing card deck icon, worn edges, simple flat 2D game UI --ar 1:1 --style raw --v 6
```

### UI-02 · 状态图标组（6个）

```
[完整性] robot integrity/health icon, simple robot silhouette with heart or structural indicator, flat 2D game UI icon, industrial style --ar 1:1 --style raw --v 6

[电量] battery charge level icon, lightning bolt or battery bar, flat 2D game UI --ar 1:1 --style raw --v 6

[过热] overheat icon, thermometer with warning symbol, orange-red accent, flat 2D game UI --ar 1:1 --style raw --v 6

[故障率] malfunction/error rate icon, gear with warning triangle, flat 2D game UI --ar 1:1 --style raw --v 6

[系统稳定] system stability icon, shield with checkmark or waveform, flat 2D game UI --ar 1:1 --style raw --v 6

[信任度] trust icon, handshake between two robot hands, flat 2D game UI --ar 1:1 --style raw --v 6
```

### UI-04 · 事件卡边框

```
industrial metal frame border design for event card, riveted steel corners, welded seam details along edges, warning stripe detail on corners, suitable for containing text and image, warm grey-brown metal tones, slight rust texture, vintage industrial aesthetic, frame only transparent center, 2D game UI element, white background showing frame shape --ar 3:4 --style raw --v 6
```

### UI-05 · 选项按钮（A/B/C）

```
chunky industrial button panel, three large square buttons labeled A B C, mechanical clicky appearance, metal housing with rubber grip edges, raised tactile design, warm brown and orange color scheme, game UI element, can be pressed/depressed states, hand-drawn cartoon style --ar 3:1 --style raw --v 6
```

### UI-06 · 任务面板（CRT风格）

```
old CRT terminal screen panel design, visible scan lines, slight screen curvature, green phosphor or amber text display, chunky plastic bezel frame, industrial computer aesthetic, suitable for displaying task information, game UI element --ar 4:3 --style raw --v 6
```

### UI-08 · Day 计数器

```
industrial dial gauge showing day counter, analog meter face reading "DAY 14", riveted metal frame, warm industrial design, slightly worn, game UI element --ar 3:2 --style raw --v 6
```

---

## 七、特效参考图（用于粒子系统参考）

> 注：特效通常不直接用AI生图，而是作为视觉参考。以下prompt用于生成参考图，实际特效在引擎内用粒子系统实现。

### FX-02 · 充电粒子参考

```
electric charging effect sparks, soft blue electrical sparks and energy bolts, flowing upward motion, particle effect reference art, dark background, energetic but not aggressive, suitable for robot charging animation reference --ar 1:1 --style raw --v 6
```

### FX-03 · 受伤火花参考

```
orange mechanical damage sparks effect, bursting outward from impact point, hot metal sparks short burst, particle effect reference, dark background, industrial machine damage aesthetic --ar 1:1 --style raw --v 6
```

### FX-08 · 背叛特效参考

```
red glitch corruption wave effect, spreading electromagnetic interference pattern, alarm red and static, dramatic warning visual effect reference, dark background --ar 16:9 --style raw --v 6
```

### FX-09 · 救赎特效参考

```
warm golden light pillar rising effect, hopeful ascending light beams, warm orange-gold particles floating upward, redemption moment visual effect reference, emotional and warm, dark background --ar 9:16 --style raw --v 6
```

### FX-10 · 电磁余波参考

```
purple electromagnetic arc effect seeping through door crack, crackling electrical tendrils, dangerous outside energy breaching shelter, dramatic atmospheric effect reference --ar 16:9 --style raw --v 6
```

---

## ─── P1 优先 ─── （Launch版）

---

## 八、场景变体

### SC-02 · 避难所室内变体（4个）

```
[服务器机房] server room bunker variant, racks of old servers with blinking lights, cable management chaos, cool blue indicator lights contrasting warm emergency lighting, underground shelter feel --ar 16:9 --style raw --v 6

[地下工厂] underground factory floor shelter, industrial machinery converted to living space, welding equipment repurposed, heavy concrete construction, warm orange work lights --ar 16:9 --style raw --v 6

[政府防卫点] former government defense post, military green and grey, maps pinned to walls, radio equipment, official insignia faded, abandoned authority atmosphere --ar 16:9 --style raw --v 6

[富人保险室] wealthy owner's luxury bunker, nicer furniture even if dusty, art on walls, better lighting, visible contrast with poverty outside, slightly opulent but post-apocalyptic --ar 16:9 --style raw --v 6
```

---

## 九、重要提示

### 风格一致性保持技巧

1. **首次生成后保存 seed**：在 Midjourney 中用 `/info` 查看 job ID，重用同一 seed 保持风格
2. **img2img 角色一致性**：生成新状态帧时，把已确认的 idle 帧上传为 style reference（`--sref`）
3. **角色 profile 参考图**：生成 3/4 侧视图作为参考，然后用 `--cref` 保持角色一致
4. **批量生成**：每个角色先生成 4 个变体（`--v 6 -q 2`），人工选最佳后再 Vary

### Midjourney 实用参数

```
--ar 3:4      → 角色 sprite 竖版
--ar 16:9     → 场景横版
--ar 1:1      → 图标方形
--style raw   → 减少 MJ 过度处理，保留原始感
--v 6         → 最新版本
--sref [URL]  → 风格参考图
--cref [URL]  → 角色一致性参考
--seed [数字] → 固定随机种子，同一 seed 生成结果相似
```

### 推荐生成顺序（7天Demo）

```
Day 2:
  1. R-03 织梦者 idle（确定外观）
  2. 避难所室内 SC-01（确定场景）
  3. 老家政 NP-01 standing
  
Day 3:
  4. R-03 全部8状态（用 --cref 保持一致）
  5. 8个资源道具图标
  6. 状态图标组
  
Day 4:
  7. UI 边框、按钮
  8. 特效参考图（给引擎粒子系统参考）
```

---

*文档版本 v1.0 · 2026-05-10*
*对应素材清单：[asset-procurement.md](asset-procurement.md)*
