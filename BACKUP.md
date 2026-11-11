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

**推送流程自己维护，不依赖 GitHub Actions。**

每次往 `main` 推新提交时，同一批操作里会把 `backup` 指向上一个提交
（也就是新 `main` 的父提交）。用的是 Contents 写权限，不需要额外授权。

具体顺序是：

1. 先把 `backup` 指到当前的 `main`
2. 再把新提交推上 `main`

两步之间 `backup` 短暂等于旧 `main`，推送完成后正好是「比 `main` 旧一格」。

### 需要注意的前提

因为这个分支是被推送流程推进的，所以：

- 通过本仓库的推送脚本 / API 推送时，`backup` 会自动跟着走。
- 直接在 GitHub 网页上编辑文件、或从别的机器 `git push`，`backup` **不会**动。
  这种情况需要手动补一次（见下）。

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
