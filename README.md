# rimworld_mod

RimWorld 1.7 mods by [liss404ng](https://github.com/liss404ng) / RimWorld 1.7 模组合集.

中文版见 [`README.zh-CN.md`](README.zh-CN.md)。

## Mods

### Stellar Provisions (Test) — [`rimworld-food-template/`](rimworld-food-template/)

**星备食品**——The Sober Conglomerate 标准配给线。一家不起眼的食品巨头，用编号、认证和格外平静的文案，照料边缘星球的一日三餐。

当前产品 / Current content:

| 编号 | 产品 | 说明 |
| --- | --- | --- |
| MR-7 | Vegetable Stew / 炖时蔬 | 简单餐档的现做正餐：0.75 营养值植物食材 → 1 份，价目与工时对齐原版 `MealSimple`（15 银 / 300）；燃料炉 / 电炉 / 营火均可制作；需烹饪 4 级；无心情加成，4 天腐坏 |
| MR-9 | Signature Casserole / 精品烩菜 | 精致餐档的浅盘封装：0.30 蛋白质 + 0.30 植物食材 → 1 份；需烹饪 6 级；吃完心情 **+5（一天）**；**8 天腐坏**（原版精致餐只有 4 天，这是差异点）；燃料炉 / 电炉 / 营火均可制作 |
| SR-1 | Long-Keep Ration / 长储配给 | 耐储配给：0.30 蛋白质 + 0.30 植物食材 → 1 份，价目对齐原版 `MealSurvivalPack`（24 银）；**永不变质**，露天放置仍会老化；需烹饪 8 级 + 包装生存食物科技 |
| SN-5 | Standard Crisps / 标准脆片 | 零食：0.25 营养值植物食材 → 8 片；**无需技能与科技**，开机即可压制；不腐烂；吃后心情 **+2 / 半天**（专属思绪） |

全部四条产品线各带一份 **×4 批量配方**：食材与产出按四倍计，工时按单做四次的 **0.8 倍**。这不是拍脑袋的数字——原版 `CookMealSurvivalBulk` 用的就是 450×4×0.8 = 1440，本 mod 的 MR-7、MR-9 与 SR-1 批量都照抄了这个值。

- Requirements: RimWorld **1.7**, Core only（无 DLC 依赖）
- Localization: English + 简体中文（内置语言包）
- Install: copy the `rimworld-food-template` folder into the game's `Mods` directory（或将本仓库克隆后拷贝该文件夹）, then enable it in the mod list.

## Docs

- [`rimworld-food-template/Docs/preferability-ladder.md`](rimworld-food-template/Docs/preferability-ladder.md) — the full `FoodPreferability` ladder (10 usable rungs, extracted from `Assembly-CSharp.dll`), which vanilla item sits on each rung, and where this mod's four products sit on it. Also covers why `DesperateOnly` is *below* raw food, and that `foodType` is a `[Flags]` enum.
- [`rimworld-food-template/Docs/tools/dump-enum.py`](rimworld-food-template/Docs/tools/dump-enum.py) — reads `.NET` metadata straight out of `Assembly-CSharp.dll` to dump any enum's member order and values, optionally counting each value's XML users under `Data/`. Needs `pip install dnfile`.

## Design notes

- Both recipes bind to workbenches via **RecipeDef-level `<recipeUsers>`**. This is a valid vanilla pattern: `ElectricTailoringBench` and `HandTailoringBench` carry no `<recipes>` block at all and are populated entirely by `recipeUsers` on `Make_Patchleather` and friends.
- Allowing **Campfire** to cook MR-7 and SR-1 is a deliberate design widening, not an oversight. Vanilla Campfire only lists `CookMealSimple`, `CookMealSimpleBulk`, `Make_Pemmican`, `Make_PemmicanBulk` and the burn bills; `CookMealSurvival` ships on the stoves only.
- SR-1 never rots because it inherits `MealBase` rather than the `MealCooked` chain — the same trick vanilla `MealSurvivalPack` uses. It is not a large `daysToRotStart`; the `CompProperties_Rottable` comp is simply absent.
- SR-1's `MarketValue` is **24**, exactly vanilla `MealSurvivalPack`. An earlier revision charged a +2 "brand premium"; it was dropped because a same-tier food priced differently just reads as a worse or better deal to the hauling and stockpile logic, and the premium belongs in the copy, not the numbers.
- MR-7 is a **simple-meal-tier** dish, not a tier of its own. An earlier revision priced it between simple and fine meals (MV 18 / WorkToMake 450); that rung does not exist in the vanilla ladder, so colonists had no reason to prefer it. It now matches `MealSimple` exactly on `MarketValue 15` / `WorkToMake 300` and keeps the inherited `optimalityOffsetHumanlikes 16`. The only deliberate deviation left is `skillRequirements Cooking 4` — `CookMealBase` has none and the vanilla gate is `Cooking 6` on `CookMealFineBase`.
- SN-5 is a **snack**, but it still has to be a food a colonist will voluntarily pick. It carries `joy 0.10` / `joyKind Gluttonous` and ships a `JoyGiverDef`, because vanilla `JoyGiver_Ingest` is an explicit `thingDefs` whitelist listing only `Chocolate` and `InsectJelly` — an item with joy values is never auto-eaten for fun without one.
- Its `preferability` is **`MealSimple`, not `DesperateOnly`**. The first release copied `Chocolate` exactly, and playtesting showed colonists would rather eat raw berries: in the vanilla preferability ladder `DesperateOnly` sits *below* raw food (`RawBerries` is `RawTasty`). `MealSimple` puts it level with `Pemmican` and above raw produce, while staying a rung below fine meals. Positive precedent for "snack that is still willingly eaten" is vanilla `InsectJelly`: a non-meal parent chain combined with `preferability MealFine`, `joy 0.08`, and `Gluttonous`.
- `foodType` stays **`Processed`** rather than `Meal`. `Meal` food eaten without a table inflicts the "ate without table" −3 mood debuff; a foil bag of crisps is meant to be eaten standing up. Note this is a combination vanilla never uses (its five `Processed` users are all drugs plus `Chocolate`), so it is worth watching in play.
- SN-5's yield ratio is not arbitrary: 0.25 nutrition in → 8 × 0.05 = 0.40 out, i.e. **1.6×**, exactly the same ratio as vanilla `Make_Pemmican` (0.5 in → 16 × 0.05 = 0.80 out). Processing amplifying nutrition is a vanilla design, not a balance bump.
- **MR-9 is the fine-meal rung, differentiated by shelf life rather than by tiles of stats.** Inheriting `MealFineBase` would have locked it to the `MealCookedIngredientless` chain's `Rottable daysToRotStart 4`, and XML inheritance cannot override a comp's property — a second `Rottable` li would just create two rot comps. So it inherits `MealBase` (no `Rottable`, the trick vanilla `MealSurvivalPack` uses) and declares its own 8-day `Rottable`. It keeps vanilla `MealFine`'s `preferability` and reuses the vanilla `AteFineMeal` thought (+5 / 1 day) instead of inventing one. The premium is paid for honestly: `MarketValue 24` vs 20, `WorkToMake 600` vs 450, ingredients 0.30+0.30 vs 0.25+0.25 (nutrition conversion 1.5× instead of 1.8×). A pure clone of `MealFine` would have been a duplicate; the longer shelf life is the only thing vanilla's fine tier cannot do.
- MR-9's bulk recipe deliberately uses the mod's uniform **0.8×** discount (1920 = 600×4×0.8) even though vanilla `CookMealFineBulk` is 1.0× (1800 = 450×4). That is internal consistency across all four lines, not a copy of the fine tier's convention.
- The **0.8× bulk discount** has a vanilla precedent rather than being a default. Vanilla batching is not uniform: `CookMealSimpleBulk` is 0.667× (1200 / 1800), `CookMealFineBulk` is 1.0× (1800 / 1800), `CookMealLavishBulk` is 1.778× (3200 / 1800), `Make_PemmicanBulk` is 1.0× (2800 / 2800), and `CookMealSurvivalBulk` is **0.8×** (1440 / 1800). The bulk recipes here follow the last one, plus the usual conventions: ingredients and products ×4, `displayPriority` = single-batch value + 10, `x4` label suffix, and bulk defs inheriting `CookMealBase` directly rather than their single-batch recipe.
- SN-5 uses **stack-count graphics** and drops `stackLimit` from `ResourceBase`'s 75 down to **20**. `Graphic_StackCount` reads a *folder* (`Textures/Things/Item/Food/Crisps/`) of `Crisps_a/_b/_c`, where the first file is one item and the last is a full stack. With three tiers, a limit of 75 would put 2–74 all on the middle image, so a small and a nearly-full pile would look identical; 20 makes the tiers readable (1 / 2–19 / full) and 20 × 0.05 nutrition = exactly one meal per cell. This is a balance tradeoff, not a hard constraint — the other two items are single-image `Graphic_Single` and stack normally.
- **Food policies enrol new foods automatically.** Vanilla stores a policy as a flat `ThingFilter.allowedDefs` snapshot captured when the policy was created, so a def added later is absent from every policy forever and `FoodUtility.WillEat` rejects it before it can even be scored — the colonist treats it as inedible and quietly walks off to eat raw produce. Vanilla has the same blind spot: `MealSimple_Veg` is missing from all ten starting policies. A Harmony postfix on `Game.FinalizeInit` **mirrors** each product's allow bit from a same-role vanilla stand-in (MR-7 and SN-5 from `MealSimple`, MR-9 from `MealFine`, SR-1 from `MealSurvivalPack`): if the stand-in is allowed so is the product, if it is forbidden so is the product. Only entries that actually disagree are written, so hand-edited policies are not overwritten on every load. This is also why the mod declares a Harmony dependency.

## Notes

- Test build — packageId `test.foodstew`; contents and balance may change. / 测试版，内容与数值仍会调整。
- Parts of this mod's XML and text were created with AI assistance. / 本 mod 的部分 XML 与文案由 AI 辅助生成。
