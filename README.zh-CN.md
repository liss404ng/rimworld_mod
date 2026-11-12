# rimworld_mod

[liss404ng](https://github.com/liss404ng) 的 RimWorld 1.7 mod 合集 / RimWorld 1.7 mods by liss404ng.

> 本文是 [`README.md`](README.md) 的中文版。两份内容保持同步，改动时请一起改。

## Mod 列表

### Stellar Provisions (Test) — [`rimworld-food-template/`](rimworld-food-template/)

**星备食品**——The Sober Conglomerate 的标准配给线。一家不起眼的食品巨头，用编号、认证和格外平静的文案，照料边缘星球的一日三餐。

当前产品：

| 编号 | 产品 | 说明 |
| --- | --- | --- |
| MR-7 | Vegetable Stew / 炖时蔬 | 简单餐档的现做正餐：0.75 营养值植物食材 → 1 份，价目与工时对齐原版 `MealSimple`（15 银 / 300）；燃料炉 / 电炉 / 营火均可制作；需烹饪 4 级；无心情加成，4 天腐坏 |
| MR-9 | Signature Casserole / 精品烩菜 | 精致餐档的浅盘封装：0.30 蛋白质 + 0.30 植物食材 → 1 份；需烹饪 6 级；吃完心情 **+5（一天）**；**8 天腐坏**（原版精致餐只有 4 天，这是差异点）；燃料炉 / 电炉 / 营火均可制作 |
| SR-1 | Long-Keep Ration / 长储配给 | 耐储配给：0.30 蛋白质 + 0.30 植物食材 → 1 份，价目对齐原版 `MealSurvivalPack`（24 银）；**永不变质**，露天放置仍会老化；需烹饪 8 级 + 包装生存食物科技 |
| SN-5 | Standard Crisps / 标准脆片 | 零食：0.25 营养值植物食材 → 8 片；**无需技能与科技**，开机即可压制；不腐烂；吃后心情 **+2 / 半天**（专属思绪） |

全部四条产品线各带一份 **×4 批量配方**：食材与产出按四倍计，工时按单做四次的 **0.8 倍**。这不是拍脑袋的数字——原版 `CookMealSurvivalBulk` 用的就是 450×4×0.8 = 1440，本 mod 的 MR-7、MR-9 与 SR-1 批量都照抄了这个值。

- 前置要求：RimWorld **1.7**，仅需 Core（无 DLC 依赖）
- 语言：英文 + 简体中文（内置语言包）
- 安装：把 `rimworld-food-template` 文件夹拷进游戏的 `Mods` 目录，然后在 mod 列表里启用。

## 文档

- [`rimworld-food-template/Docs/preferability-ladder.md`](rimworld-food-template/Docs/preferability-ladder.md) —— 完整的 `FoodPreferability` 阶梯（10 个可用档位，从 `Assembly-CSharp.dll` 中提取）、每个档位上有哪些原版物品，以及本 mod 四件产品各站在哪一级。文中也解释了为什么 `DesperateOnly` **低于**生食，以及 `foodType` 是一个 `[Flags]` 枚举。
- [`rimworld-food-template/Docs/tools/dump-enum.py`](rimworld-food-template/Docs/tools/dump-enum.py) —— 直接从 `Assembly-CSharp.dll` 读 `.NET` 元数据，导出任意枚举的成员顺序与数值，并可选统计每个取值在 `Data/` 下的 XML 使用者数量。需要 `pip install dnfile`。

## 设计说明

- **设计前先查阅 `rimworld-modding` skill。** 本 mod 的每一件产品都是先打开该 skill 再动笔的——先看它的模板库与三层决策（有模板就直接用；没有模板就先对照原版 `Data/Core` 核验再写；绝不凭记忆猜字段名或枚举值）。命名规范、`<ModMetaData>` 写法与贴图尺寸也按同一套约定执行。本文的数值之所以都带原版文件与行号出处，就是这条规矩的结果。
- 两份配方都通过 **RecipeDef 级的 `<recipeUsers>`** 挂到工作台上。这是原版就有的合法写法：`ElectricTailoringBench` 与 `HandTailoringBench` 完全没有 `<recipes>` 块，它们的配方表全部由 `Make_Patchleather` 这类配方上的 `recipeUsers` 填出来。
- 允许 **营火** 制作 MR-7、MR-9 与 SR-1 是**有意的设计放宽**，不是疏漏。原版营火只列了 `CookMealSimple`、`CookMealSimpleBulk`、`Make_Pemmican`、`Make_PemmicanBulk` 和几个焚烧账单；`CookMealSurvival` 只在炉子上。
- SR-1 永不变质，是因为它继承的是 `MealBase`，而不是 `MealCooked` 那条链——原版 `MealSurvivalPack` 用的同一招。它**不是**把 `daysToRotStart` 调得特别大，而是根本没有 `CompProperties_Rottable` 这个 comp。
- SR-1 的 `MarketValue` 是 **24**，与 `MealSurvivalPack` 一字不差。早先的版本收过 +2 的「品牌溢价」；那个改动被撤掉了，因为同档位食物定不同的价，在搬运与库存逻辑看来只是「更划算」或「更不划算」，溢价应该写在文案里，不该写在数字里。
- MR-7 是**简单餐档**的菜，不是自成一档。早先版本把它定价在简单餐与精致餐之间（MV 18 / WorkToMake 450）；原版阶梯里并不存在那个档位，所以小人没有任何理由偏好它。现在它精确匹配 `MealSimple` 的 `MarketValue 15` / `WorkToMake 300`，并保留了继承来的 `optimalityOffsetHumanlikes 16`。唯一有意保留的偏离是 `skillRequirements Cooking 4`——`CookMealBase` 本身没有技能门槛，原版的门槛是 `CookMealFineBase` 上的 `Cooking 6`。
- **MR-9 是精致餐档，靠保质期而不是堆数值来做差异。** 如果直接继承 `MealFineBase`，就会被锁在 `MealCookedIngredientless` 链的 `Rottable daysToRotStart 4` 上，而 XML 继承**无法覆盖**已有 comp 的属性——再加一个 `Rottable` li 只会变成两条腐烂组件。所以它继承 `MealBase`（不含 `Rottable`，原版 `MealSurvivalPack` 用的同一招），自己声明 8 天的 `Rottable`；`preferability` 保持 `MealFine`，并**复用原版 `AteFineMeal` 思绪**（+5 / 1 天）而不另造。溢价是实付的：`MarketValue 24`（原版 20）、`WorkToMake 600`（原版 450）、食材 0.30+0.30（原版 0.25+0.25，营养转化 1.5× 对 1.8×）。纯克隆 `MealFine` 只会是多一件重复品，而「更长的保质期」正是原版精致餐档做不到的事。
- MR-9 的批量配方**刻意**沿用本 mod 统一的 0.8×（1920 = 600×4×0.8），尽管原版 `CookMealFineBulk` 是 1.0×（1800 = 450×4）。这是四条线之间的内部一致性，不是照抄精致餐档的惯例。
- SN-5 是**零食**，但它仍然必须是小人**会主动去拿**的食物。它带 `joy 0.10` / `joyKind Gluttonous`，并自带一个 `JoyGiverDef`——因为原版 `JoyGiver_Ingest` 是一份显式的 `thingDefs` 白名单，里面只有 `Chocolate` 和 `InsectJelly`。一个带 joy 数值、却没有对应 JoyGiver 的物品，**永远不会**被主动拿去吃着玩。
- 它的 `preferability` 是 **`MealSimple`，不是 `DesperateOnly`**。最初的版本完全照抄 `Chocolate`，实测结果是小人宁可去啃生浆果：在原版阶梯里 `DesperateOnly` 排在生食**之下**（`RawBerries` 是 `RawTasty`）。`MealSimple` 让它与 `Pemmican` 同级、高于生鲜，同时仍比精致餐低一档。「零食但仍然愿意吃」的正面前例是原版 `InsectJelly`：非餐食的 parent 链，配 `preferability MealFine`、`joy 0.08`、`Gluttonous`。
- `foodType` 保持 **`Processed`** 而不改成 `Meal`。`Meal` 类食物在没桌子时吃会吃出「无桌进食」−3 心情；一袋铝箔装的脆片本来就该站着吃。需要注意这是原版从未用过的组合（原版五个 `Processed` 使用者全是毒品加一个 `Chocolate`），所以值得在实机里盯着。
- SN-5 的产出比不是随手定的：0.25 营养入 → 8 × 0.05 = 0.40 出，即 **1.6×**，与 `Make_Pemmican` 的比例完全相同（0.5 入 → 16 × 0.05 = 0.80 出）。加工会放大营养，这是原版的设计，不是数值buff。
- **0.8 倍的批量折扣**有原版先例，不是默认值。原版的批量化并不统一：`CookMealSimpleBulk` 是 0.667×（1200 / 1800），`CookMealFineBulk` 是 1.0×（1800 / 1800），`CookMealLavishBulk` 是 1.778×（3200 / 1800），`Make_PemmicanBulk` 是 1.0×（2800 / 2800），`CookMealSurvivalBulk` 是 **0.8×**（1440 / 1800）。本 mod 的批量配方跟随最后一种，并遵守其余惯例：食材与产出 ×4、`displayPriority` = 单次值 + 10、label 加 `x4` 后缀、批量 def 直接继承 `CookMealBase` 而非各自的单次配方。
- SN-5 使用**堆叠贴图**，并把 `stackLimit` 从 `ResourceBase` 的 75 降到 **20**。`Graphic_StackCount` 读取的是一个**文件夹**（`Textures/Things/Item/Food/Crisps/`）里的 `Crisps_a/_b/_c`，第一个文件是单件、最后一个是满堆。只有三档的情况下，上限 75 会让 2～74 全落在中间那张图上，一小把和快要满了看起来一模一样；20 让三个档位都能读出来（1 / 2～19 / 满），而且 20 × 0.05 营养 = 每格正好一餐。这是数值上的取舍，不是硬性限制——另外三件产品是单图 `Graphic_Single`，按常规堆叠。
- 饮食策略会自动登记。原版把「允许的食物」存成一份**策略创建当时的名单快照**（`ThingFilter.allowedDefs`），之后新增的食物永远不会自己进去，`FoodUtility.WillEat` 会直接把它拒掉——小人于是当作你不能吃。原版自己也有这个漏洞（`MealSimple_Veg` 在全部 10 条初始策略里都不存在）。本 mod 在 `Game.FinalizeInit` 上挂了个 Harmony 补丁，按原版同档位的对应食物（MR-7 与 SN-5 对应 `MealSimple`，MR-9 对应 `MealFine`，SR-1 对应 `MealSurvivalPack`）**镜像**允许位：对应食物被允许，新产品就被允许；被禁止就一起禁止。只在数值不一致时才写入，所以手改过的策略不会被反复覆盖。这也是本 mod 声明 Harmony 依赖的原因。
- **今后食物贴图统一用 640×640。** 这是本仓库的家规，不是原版要求，而且它安全的原因值得写清楚：`GraphicData.drawSize` 默认是 `Vector2.one`，原版没有任何食物 Def 覆写它，所以 640 的画布和 128 的画布在屏幕上占的是**一模一样大**——画布尺寸买的是分辨率，永远不是大小。原版自己也不统一：把 `Assets.zip` 里 57 张餐食贴图全部量一遍，640×640 有 27 张（`Meal/Fine`、`Meal/Lavish`、`Meal/NutrientPaste`，都带 10 级 mip），128×128 有 18 张（`Meal/Simple`、`Meal/SurvivalPack`、`Meal/FineVeg`、`Meal/FineMeat`、`Meal/LavishVeg`、`Meal/LavishMeat`），64×64 有 12 张（Simple 与 SurvivalPack 的 `_m_`／`_v_` 肉素变体）；资源型食物则一律 64×64（`Chocolate`、`Pemmican`、`InsectJelly`、`Berries`）。我们取最高那一档，成品美术才有余量，也才与「精致餐档」被拿来对比的原版资产同规格。已发布的四件产品仍带着各自的 128×128 占位图，等正式美术到位时按 640 重新导出即可，**不需要改任何 Def**。
- **贴图只做占位，这是有意为之。** 每件产品配一张 640×640 的 RGBA 占位图：路径对、画布尺寸对、堆叠档位形状对，但除了能辨认的轮廓之外不投入任何美术功夫。成品贴图由作者自行绘制并覆盖占位图——Def 只依赖文件的**尺寸**和**文件夹形状**，不依赖画面内容。新产品必须遵守的约定：单图物品是 `Textures/Things/Item/Food/<Name>.png` 一个文件，配 `Graphic_Single`；堆叠物品是一个文件夹 `Textures/Things/Item/Food/<Name>/`，里面放 `<Name>_a` / `_b` / `_c`，配 `Graphic_StackCount`，第一个文件是单件、最后一个是满堆。这三张保持同一个画布（640×640）——`Graphic_StackCount.SubGraphicForStackCount` 是按 `stackCount == 1` / `== stackLimit` / 中间值三档切换的，尺寸不一致会在堆叠数变化时肉眼可见地跳一下。
## 备注

- 测试版 —— packageId `test.foodstew`；内容与数值仍会调整。
- 本 mod 的部分 XML 与文案由 AI 辅助生成。
