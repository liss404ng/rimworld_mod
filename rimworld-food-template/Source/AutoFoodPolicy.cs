// AI 辅助生成
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace StellarProvisions
{
    /// <summary>
    /// RimWorld stores a food policy as a flat HashSet of allowed ThingDefs captured when the
    /// policy was created (ThingFilter.allowedDefs). A def that did not exist yet at that moment
    /// is therefore absent from every policy, and FoodUtility.WillEat rejects it outright:
    /// the food never even reaches the candidate list. Vanilla has the same blind spot
    /// (MealSimple_Veg is missing from all ten starting policies).
    ///
    /// This sync mirrors each product's allow bit from a vanilla stand-in with the same role,
    /// once per game load. It is deliberately idempotent: if the stand-in is allowed, so is the
    /// product; if it is not, neither is. A policy that forbids ordinary simple meals
    /// keeps forbidding these.
    /// </summary>
    public static class FoodPolicyAutoEnroll
    {
        private static readonly string[][] Map =
        {
            new[] { "TST_Food_MR7_VegetableStew", "MealSimple" },
            new[] { "TST_Food_SR1_LongKeepRation", "MealSurvivalPack" },
            new[] { "TST_Food_SN5_StandardCrisps", "MealSimple" },
            new[] { "TST_Food_MR9_SignatureCasserole", "MealFine" },
        };

        private static Game doneFor;

        public static void Run(Game game)
        {
            if (game == null || game == doneFor)
            {
                return;
            }
            var db = game.foodRestrictionDatabase;
            if (db == null)
            {
                return;
            }
            doneFor = game;

            var products = new List<ThingDef>();
            var proxies = new List<ThingDef>();
            foreach (string[] pair in Map)
            {
                ThingDef product = DefDatabase<ThingDef>.GetNamedSilentFail(pair[0]);
                ThingDef proxy = DefDatabase<ThingDef>.GetNamedSilentFail(pair[1]);
                products.Add(product);
                proxies.Add(proxy);
            }

            int policies = 0, changed = 0;
            foreach (var policy in db.AllFoodRestrictions)
            {
                var filter = policy.filter;
                if (filter == null)
                {
                    continue;
                }
                policies++;
                for (int i = 0; i < products.Count; i++)
                {
                    ThingDef product = products[i];
                    ThingDef proxy = proxies[i];
                    if (product == null || proxy == null)
                    {
                        continue;
                    }
                    bool shouldAllow = filter.Allows(proxy);
                    if (filter.Allows(product) != shouldAllow)
                    {
                        filter.SetAllow(product, shouldAllow);
                        changed++;
                    }
                }
            }

            Log.Message("[Stellar Provisions] food policies synced: " + policies +
                        " policies, " + changed + " entries adjusted.");
        }
    }

    [HarmonyPatch(typeof(Game), "FinalizeInit")]
    public static class Patch_Game_FinalizeInit
    {
        public static void Postfix(Game __instance)
        {
            FoodPolicyAutoEnroll.Run(__instance);
        }
    }

    /// <summary>
    /// Game.FinalizeInit runs before GameComponentUtility.LoadedGame, so a GameComponent's
    /// ExposeData has already restored the saved policies by then. Registering the write as a
    /// component would also work, but the component is created inside the ExposeData loop and
    /// would need its own guard; the Harmony postfix keeps the hook in one place.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class Bootstrap
    {
        static Bootstrap()
        {
            new Harmony("liss404ng.stellarprovisions").PatchAll();
            Log.Message("[Stellar Provisions] Harmony patches applied.");
        }
    }
}
