# 备份分支

`backup` 分支保存**上一个版本**的仓库状态：每当 `main` 有新提交，
`backup` 就向后移动一格，指向那次推送的父提交。

```
main     A → B → C → D     （当前）
backup       ↑   ↑   ↑
             A   B   C     （总是落后一个版本）
```

## 为什么这么做

`main` 上直接改坏了，`backup` 里一定是改坏之前的样子。
它不会和 `main` 指向同一个提交——那等于没有备份。

## 谁在维护它

**GitHub Actions 自动维护。** `.github/workflows/backup.yml` 在每次
`push` 到 `main` 时触发，读取这次推送的父提交，把 `backup` force 到那个提交。
第一次运行会创建分支。

推送脚本里也做了同样的 rollback（`push-mod.ps1` 与 `push-api.ps1`）。
两边都做是有意的冗余：脚本那步保证 API 推送时也立刻正确，workflow 那步
保证网页编辑、别的机器推送、或者直接改文件时也会被兜住。重复推同一个
sha 是幂等的，无害。

### 需要注意的前提

- Actions 长时间没有提交会被 GitHub 自动停用。去仓库的 Actions 页面点一下
  Enable workflow，或手动跑一次 `workflow_dispatch` 即可恢复。
- Actions 跑的时候是异步的，刚 push 完的几秒内 `backup` 可能还没动。
  等它跑完再看，或者用下面的手动命令立刻对齐。

手动把 `backup` 对齐到 `main` 的父提交：

```bash
git fetch origin
git push origin "$(git rev-parse origin/main^):backup" --force
```

## 怎么用

看上一版有什么：

```bash
git fetch origin
git diff backup main --stat
```

从上一版里取回一个文件：

```bash
git checkout backup -- rimworld-food-template/Defs/ThingDefs/Food_MR7_VegetableStew.xml
```

整个仓库回到上一版（会丢掉当前未提交的改动，谨慎）：

```bash
git reset --hard backup
```

## 注意

- `backup` 永远**只有一格深度**，它不保留更早的历史。要取更早的版本得用 `main` 的提交历史或 `git reflog`。
- 只备份到这个仓库自己，没有异地副本。仓库本身被删就一起没了。
- 它备份的是**提交**，不是你本地还没提交的工作区改动。
