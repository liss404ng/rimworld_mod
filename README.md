# rimworld_mod

RimWorld 1.7 mods by [liss404ng](https://github.com/liss404ng) / RimWorld 1.7 模组合集。

## Mods

### Stellar Provisions (Test) — [`rimworld-food-template/`](rimworld-food-template/)

**星备食品**——The Sober Conglomerate 标准配给线。一家不起眼的食品巨头，用编号、认证和格外平静的文案，照料边缘星球的一日三餐。

当前产品 / Current content:

| 编号 | 产品 | 说明 |
| --- | --- | --- |
| MR-7 | Vegetable Stew / 炖时蔬 | 定位在简单餐与精致餐之间的现做正餐：0.75 营养值植物食材 → 1 份；燃料炉 / 电炉 / 营火均可制作；需烹饪 4 级；无心情加成，4 天腐坏 |
| SR-1 | Long-Keep Ration / 长储配给 | 耐储配给：0.30 蛋白质 + 0.30 植物食材 → 1 份；**永不变质**，露天放置仍会老化；需烹饪 8 级 + 包装生存食物科技 |
| SN-5 | Standard Crisps / 标准脆片 | 零食：0.25 营养值植物食材 → 8 片；**无需技能与科技**，开机即可压制；不腐烂；吃后心情 **+2 / 半天**（专属思绪） |

- Requirements: RimWorld **1.7**, Core only（无 DLC 依赖）
- Localization: English + 简体中文（内置语言包）
- Install: copy the `rimworld-food-template` folder into the game's `Mods` directory（或将本仓库克隆后拷贝该文件夹）, then enable it in the mod list.

## Design notes

- Both recipes bind to workbenches via **RecipeDef-level `<recipeUsers>`**. This is a valid vanilla pattern: `ElectricTailoringBench` and `HandTailoringBench` carry no `<recipes>` block at all and are populated entirely by `recipeUsers` on `Make_Patchleather` and friends.
- Allowing **Campfire** to cook MR-7 and SR-1 is a deliberate design widening, not an oversight. Vanilla Campfire only lists `CookMealSimple`, `CookMealSimpleBulk`, `Make_Pemmican`, `Make_PemmicanBulk` and the burn bills; `CookMealSurvival` ships on the stoves only.
- SR-1 never rots because it inherits `MealBase` rather than the `MealCooked` chain — the same trick vanilla `MealSurvivalPack` uses. It is not a large `daysToRotStart`; the `CompProperties_Rottable` comp is simply absent.
- MR-7 sits between the simple and fine meal tiers on purpose: `CookMealBase` has no `skillRequirements`, the vanilla gate is `Cooking 6` on `CookMealFineBase`, so `Cooking 4` fills the gap.
- SN-5 is a **joy item, not a meal**. It uses `preferability DesperateOnly` and carries `joy 0.10` / `joyKind Gluttonous`, copying vanilla `Chocolate` exactly — a colonist will only eat it as food when starving, but will seek it out for recreation. This is why it ships a `JoyGiverDef`: vanilla `JoyGiver_Ingest` is an explicit `thingDefs` whitelist listing only `Chocolate` and `InsectJelly`, so an item with joy values is never auto-eaten without one.
- SN-5's yield ratio is not arbitrary: 0.25 nutrition in → 8 × 0.05 = 0.40 out, i.e. **1.6×**, exactly the same ratio as vanilla `Make_Pemmican` (0.5 in → 16 × 0.05 = 0.80 out). Processing amplifying nutrition is a vanilla design, not a balance bump.

## Notes

- Test build — packageId `test.foodstew`; contents and balance may change. / 测试版，内容与数值仍会调整。
- Parts of this mod's XML and text were created with AI assistance. / 本 mod 的部分 XML 与文案由 AI 辅助生成。
