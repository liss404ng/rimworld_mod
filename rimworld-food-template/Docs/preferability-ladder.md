# FoodPreferability 阶梯（RimWorld 1.7）

小人「愿意吃什么」由 `ThingDef/ingestible/preferability` 决定，取值是一个有序枚举
`RimWorld.FoodPreferability`。**数值越大越优先**：饥饿的小人会在可达食物里挑数值最高的那个。

本文件不是抄文档，是用 `Docs/tools/dump-enum.py` 直接从 `Assembly-CSharp.dll` 的 .NET
元数据表里读出来的定义顺序，再用 `--with-users` 统计原版 XML 的实际使用者。

复现：

```bash
python Docs/tools/dump-enum.py FoodPreferability --with-users --data-root "<RimWorld>/Data"
```

## 完整阶梯（11 个成员，实际可用 10 档）

| 值 | 成员 | 含义 | 原版使用者 |
|---:|---|---|---|
| 0 | `Undefined` | 默认占位，不该有人用 | 0 处 |
| 1 | `NeverForNutrition` | 完全不算食物，只在极端场合被吃 | 6 处（药丸类 `DrugBases.xml:35`、`Odyssey` 的水生植物等） |
| 2 | `DesperateOnly` | 弹尽粮绝才吃 | 8 处（`Ambrosia.xml:30`、Chocolate `Items_Luxury.xml:28`、`Biotech` 婴儿食品等） |
| 3 | `DesperateOnlyForHumanlikes` | 同上，且只对类人生物如此 | 1 处（`Items_Resource_RawPlant.xml:184`，干草一类：动物能吃、人不能） |
| 4 | `RawBad` | 生食，难吃但能吃 | 7 处（Kibble `Items_Food.xml:285`、`Items_Resource_RawPlant.xml:20` 等） |
| 5 | `RawTasty` | 生食，但味道不错 | 2 处（`Items_Resource_AnimalProduct.xml:31`、**RawBerries** `Items_Resource_RawPlant.xml:173`） |
| 6 | `MealTerrible` | 做熟的，但难以下咽 | 1 处，**仅 Biotech DLC**（BabyFood `Biotech/.../Items_Food.xml:24`）；Core 无人使用 |
| 7 | `MealAwful` | 做熟的，勉强算饭 | 1 处（营养膏 `Items_Food.xml:92`） |
| 8 | `MealSimple` | 普通一餐 | 3 处（`MealSimple:139`、**Pemmican:324**、`MealSurvivalPack:70`） |
| 9 | `MealFine` | 精致餐 | 2 处（`MealFineBase:153`、**InsectJelly** `Items_Resource_AnimalProduct.xml:59`） |
| 10 | `MealLavish` | 奢侈餐 | 1 处（`MealLavish:216`） |

> 没有 `Gourmet` 这个成员——在 DLL 字符串里 0 次命中，是常见误传。

## 两条容易踩的坑

**1. `DesperateOnly` 比生食还低。**
生浆果是 `RawTasty`（5），`DesperateOnly` 是 2。所以给零食写 `DesperateOnly`，小人会放着
零食不吃、去啃路边的生浆果——这不是 bug，是它在偏好阶梯上真的排在生食后面。本 mod 的
SN-5 就踩过这个坑（早期照抄 Chocolate），已改为 `MealSimple`。

**2. 「零食」和「会被主动选择」不冲突。**
`InsectJelly` 是正面样板：它继承 `OrganicProductBase`（不是任何 Meal 链）、不腐烂、
走 `Graphic_StackCount`，却同时写了 `preferability MealFine` + `joy 0.08` +
`joyKind Gluttonous`。也就是说物品可以既是零食、又能当正餐吃、还能提供娱乐。

## 本 mod 三样食物落在哪

| 产品 | preferability | 原版对照 | 说明 |
|---|---|---|---|
| MR-7 炖时蔬 | `MealSimple` (8) | 原版 `MealSimple` | 价目、工时、偏好档全部对齐简单餐 |
| SR-1 长储配给 | `MealSimple` (8) + `optimalityOffsetHumanlikes -5` | 原版 `MealSurvivalPack` | 同档但轻微降权，所以小人优先拿新鲜菜而不是配给 |
| SN-5 标准脆片 | `MealSimple` (8) | 介于 Pemmican 与 InsectJelly 之间 | `foodType Processed` 让它站着吃（不进桌子，也就没有「吃饭没桌子」−3 心情） |

## 附：`foodType` 是 Flags，不是有序枚举

`ingestible/foodType` 的底层类型是 `RimWorld.FoodTypeFlags`，标了 `[Flags]`。
所以它既有基础位，也有原版预先拼好的组合值——看到 `4097` 这种数字不要以为出错了：

```
   1  VegetableOrFruit      2  Meat              4  Fluid           8  Corpse
  16  Seed                 32  AnimalProduct    64  Plant         128  Tree
 256  Meal                512  Processed       1024  Liquor       2048  Kibble
4096  Fungus
4097  VegetarianAnimal  = Fungus | VegetableOrFruit
8017  VegetarianRoughAnimal                    2826  CarnivoreAnimal
  10  CarnivoreAnimalStrict = Meat | Corpse     7963  OmnivoreAnimal
8027  OmnivoreRoughAnimal                      6801  DendrovoreAnimal
2848  OvivoreAnimal                            7999  OmnivoreHuman
```

实际使用只需在 XML 里写组合值自己的名字（`<foodType>VegetarianAnimal</foodType>`），
不要手写按位或的结果。

## 想调档位时改哪里

- **往上**：只能到 `MealFine`(9) / `MealLavish`(10)。到 `MealFine` 时原版会给 `tasteThought
  AteFineMeal`，需要自己补 `tasteThought`，否则拿不到那份心情。
- **往下**：`MealAwful`(7) 是「能吃但不情愿」，营养膏就是这一档。
- **细调优先级**（不想动档位时）：`optimalityOffsetHumanlikes` 是同一档位内的微调，
  `MealSurvivalPack` 用 `-5` 把配给压在新鲜菜之后；`MealBaseIngredientless` 默认 `+16`。
  本 mod 的 MR-7/SR-1 继承链分别拿到 `16` 和 `-5`，不要随手覆写。
- **别混用**：`foodType` 改 `Meal` 会让小人吃饭必须找桌子，没桌子吃出 −3 心情。
  想「站着吃」就保持非 `Meal` 的 `foodType`。
