#!/usr/bin/env python3
"""
一键初始化哲学家知识蒸馏项目目录结构。

用法:
    python init_project.py {philosopher} [output_dir]

示例:
    python init_project.py Nietzsche ./philosopher_corpus/Nietzsche/
    python init_project.py 庄子
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime


def init_project(philosopher: str, output_dir: str = None):
    """创建完整的项目目录结构和初始配置文件。"""

    if output_dir is None:
        output_dir = f"./philosopher_corpus/{philosopher}/"

    root = Path(output_dir).resolve()
    dirs = [
        root / "raw_corpus" / "primary",
        root / "raw_corpus" / "secondary" / "tier1",
        root / "raw_corpus" / "secondary" / "tier2",
        root / "raw_corpus" / "secondary" / "tier3",
        root / "cleaned_corpus" / "primary",
        root / "cleaned_corpus" / "secondary" / "tier1",
        root / "cleaned_corpus" / "secondary" / "tier2",
        root / "cleaned_corpus" / "secondary" / "tier3",
        root / "distill_ready",
        root / "logs",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [创建] {d.relative_to(root)}")

    # 创建项目配置模板
    config = {
        "philosopher": philosopher,
        "created_at": datetime.now().isoformat(),
        "phases": {
            "1": {"status": "pending", "resources_found": 0},
            "2": {"status": "pending", "files_downloaded": 0},
            "3": {"status": "pending", "primary_cleaned": 0, "secondary_cleaned": 0},
            "3.5": {"status": "pending", "conflicts_detected": 0},
            "4": {"status": "pending", "format": "pending"},
            "5": {"status": "pending"},
        }
    }

    config_path = root / "project_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"  [创建] {config_path.name}")

    # 创建 .gitignore
    gitignore = root / ".gitignore"
    gitignore.write_text(
        "raw_corpus/\n"
        "cleaned_corpus/\n"
        "distill_ready/\n"
        "logs/\n"
        "*.pdf\n"
        "*.epub\n"
        "*.html\n"
        "__pycache__/\n"
        ".env\n"
    )
    print(f"  [创建] {gitignore.name}")

    print(f"\n✅ 项目已初始化: {root}")
    print(f"   哲学家: {philosopher}")
    print(f"   下一步: 运行 Phase 1 数据源检索")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python init_project.py {philosopher} [output_dir]")
        sys.exit(1)

    philosopher = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    init_project(philosopher, output_dir)
