#!/usr/bin/env python3
"""
dump-enum.py — 从 RimWorld 的 Assembly-CSharp.dll 里导出 .NET 枚举的定义顺序与数值。

为什么需要它：
    RimWorld 的很多枚举（FoodPreferability、FoodType、JoyKind …）只在 DLL 里，
    XML 里只能看到「用过哪些值」，看不到「一共有哪些值、谁高谁低」。
    靠猜顺序会直接导致 mod 行为错误 —— 本仓库就踩过一次坑：
    SN-5 脆片照抄 Chocolate 用了 DesperateOnly，实测小人宁可啃生浆果，
    因为在偏好阶梯里 DesperateOnly(2) 低于生浆果的 RawTasty(5)。

依赖：
    python -m pip install dnfile

用法：
    python dump-enum.py FoodPreferability
    python dump-enum.py FoodTypeFlags
    python dump-enum.py FoodPreferability --dll "D:/其他路径/Assembly-CSharp.dll"
    python dump-enum.py FoodPreferability --with-users   # 额外统计 Data/ 下各值的 XML 使用处

默认 DLL 路径按 Windows 常见 Steam 安装位置猜测，可用 --dll 或环境变量 RIMWORLD_DLL 覆盖。

注意（踩过的坑）：
  1. 不要用 [System.Reflection.Assembly]::LoadFrom 去加载这个 DLL —— RimWorld 是
     Mono 编译的，在 .NET Core 的 PowerShell 7 里会因 System.Private.CoreLib 缺失而失败。
     必须走元数据解析（dnfile）或 Mono.Cecil。
  2. dnfile 的 TypeDefRow.FieldList 返回的是 **list**，不是单个索引；
     要写 row.FieldList[0].row_index 才拿得到起始字段行号。
  3. 枚举常量存在 Constant 表里，用 Parent.row_index 关联到 Field 行；
     Constant.Value 是 HeapItemBinary，要 .value 取 bytes 再按小端有符号整数解码。
"""

import argparse
import os
import struct
import sys

# Windows 控制台默认 GBK，中文提示会变乱码；统一改 UTF-8 输出。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

DEFAULT_DLL_CANDIDATES = [
    r"D:\soft\steam\steamapps\common\RimWorld\Assembly-CSharp.dll",
    r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Assembly-CSharp.dll",
    r"/home/user/.steam/steam/steamapps/common/RimWorld/Assembly-CSharp.dll",
]


def find_dll(explicit):
    if explicit:
        return explicit
    env = os.environ.get("RIMWORLD_DLL")
    if env:
        return env
    for p in DEFAULT_DLL_CANDIDATES:
        if os.path.isfile(p):
            return p
    return None


def load(dll_path):
    try:
        import dnfile
    except ImportError:
        sys.exit("缺少依赖 dnfile，请先执行：python -m pip install dnfile")
    return dnfile.dnPE(dll_path)


def decode_constant(const_row):
    """Constant.Value 是 HeapItemBinary；取 .value 后按小端有符号整数解码。"""
    v = const_row.Value
    raw = getattr(v, "value", v)
    if isinstance(raw, (bytes, bytearray)):
        if len(raw) == 0:
            return None
        return int.from_bytes(raw, "little", signed=True)
    return raw


def field_start(typedef_row):
    """FieldList 是 list，取第一个元素的 row_index；空表返回 None。"""
    fl = typedef_row.FieldList
    if not fl:
        return None
    return fl[0].row_index


def dump_enum(pe, enum_name):
    md = pe.net.mdtables
    tds = md.TypeDef.rows
    fields = md.Field.rows
    consts = md.Constant.rows

    target = None
    for i, row in enumerate(tds):
        if str(row.TypeName) == enum_name:
            target = i
            break
    if target is None:
        return None

    namespace = str(tds[target].TypeNamespace)
    start = field_start(tds[target])
    if start is None:
        return None

    # 结束边界：向后找第一个「有字段」的 TypeDef。不能直接取 target+1 ——
    # 枚举若正好是元数据表最后一项，target+1 越界，会把整张字段表都 dump 出来。
    end = None
    for j in range(target + 1, len(tds)):
        s = field_start(tds[j])
        if s is not None and s > start:
            end = s
            break
    if end is None:
        # 没有后继类型：用本类型字段数兜底，而不是 len(fields)+1
        end = start + max(1, len(tds[target].FieldList or []))

    # Constant 行按 Parent(Field 行号) 建索引
    const_map = {}
    for c in consts:
        try:
            if c.Parent.table.name != "Field":
                continue
            const_map[c.Parent.row_index] = c
        except (AttributeError, TypeError):
            continue

    members = []
    for idx in range(start, end):
        f = fields[idx - 1]
        name = str(f.Name)
        if name == "value__":
            underlying = const_map.get(idx)
            raw = decode_constant(underlying) if underlying else None
            # value__ 的常量如果是字节宽度，说明底层类型宽度；这里只用于提示
            members.append(("__underlying__", name, raw))
            continue
        c = const_map.get(idx)
        val = decode_constant(c) if c else None
        members.append((namespace, name, val))

    return members


def count_xml_users(data_root, values):
    """统计 Data/ 下所有 XML 里 <preferability>值</preferability> 的出现次数与位置。"""
    import re

    pat = re.compile(r"<(?:preferability|foodType|joyKind)>([A-Za-z_][A-Za-z0-9_]*)</(?:preferability|foodType|joyKind)>")
    counts = {v: [] for v in values}
    for dirpath, _dirnames, filenames in os.walk(data_root):
        for fn in filenames:
            if not fn.lower().endswith(".xml"):
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                    for lineno, line in enumerate(fh, 1):
                        for m in pat.finditer(line):
                            val = m.group(1)
                            if val in counts:
                                counts[val].append((os.path.relpath(full, data_root), lineno))
            except OSError:
                continue
    return counts


def main():
    ap = argparse.ArgumentParser(description="导出 RimWorld DLL 中的枚举定义顺序与数值")
    ap.add_argument("enums", nargs="+", help="枚举类型名，如 FoodPreferability")
    ap.add_argument("--dll", help="Assembly-CSharp.dll 路径")
    ap.add_argument("--with-users", action="store_true",
                    help="额外统计 RimWorld Data/ 目录下 XML 里各取值的出现位置")
    ap.add_argument("--data-root", default=None,
                    help="RimWorld Data 目录（默认由 DLL 路径推得）")
    args = ap.parse_args()

    dll = find_dll(args.dll)
    if not dll or not os.path.isfile(dll):
        sys.exit("找不到 Assembly-CSharp.dll，请用 --dll 指定，或设置环境变量 RIMWORLD_DLL")

    print(f"DLL: {dll}\n")
    pe = load(dll)

    for enum_name in args.enums:
        members = dump_enum(pe, enum_name)
        if members is None:
            print(f"!! 未找到枚举 {enum_name}")
            continue

        real = [(ns, n, v) for ns, n, v in members if ns != "__underlying__"]
        print(f"=== {enum_name} ===  ({len(real)} 个成员)")
        for ns, name, val in real:
            print(f"  {str(val):>4}  {name}")

        if args.with_users:
            data_root = args.data_root
            if not data_root:
                # <game>/Assembly-CSharp.dll -> <game>/Data
                data_root = os.path.join(os.path.dirname(dll), "Data")
            if os.path.isdir(data_root):
                counts = count_xml_users(data_root, [n for _ns, n, _v in real])
                print(f"  --- XML 使用统计（{data_root}） ---")
                for _ns, name, _val in real:
                    hits = counts.get(name, [])
                    if not hits:
                        print(f"    {name:<32} 0 处")
                    else:
                        sample = ", ".join(f"{p}:{ln}" for p, ln in hits[:3])
                        more = "" if len(hits) <= 3 else f" (+{len(hits)-3})"
                        print(f"    {name:<32} {len(hits)} 处  {sample}{more}")
            else:
                print(f"  (未找到 Data 目录：{data_root})")
        print()


if __name__ == "__main__":
    main()
