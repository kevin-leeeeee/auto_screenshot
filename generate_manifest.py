#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manifest Generator for AutoFlow Control Center
生成版本資訊清單,用於智慧更新檢測
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

# 版本資訊
VERSION_FILE = Path("version.txt")
CORE_VERSION_FILE = Path("core_version.txt")
SCRIPTS_VERSION_FILE = Path("scripts_version.txt")

# 建置產物
DIST_DIR = Path("dist")

# GitHub Repository
REPO_NAME = "kevin-leeeeee/auto_screenshot"


def calculate_sha256(file_path: Path) -> str:
    """計算檔案的 SHA256 雜湊值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_size(file_path: Path) -> int:
    """取得檔案大小 (bytes)"""
    return file_path.stat().st_size


def read_version(file_path: Path) -> str:
    """讀取版本號"""
    if file_path.exists():
        return file_path.read_text().strip()
    return "unknown"


def generate_manifest():
    """生成 manifest.json"""
    
    # 讀取版本號
    version = read_version(VERSION_FILE)
    core_version = read_version(CORE_VERSION_FILE)
    scripts_version = read_version(SCRIPTS_VERSION_FILE)
    
    print(f"📦 生成 Manifest for v{version}")
    print(f"   核心版本: v{core_version}")
    print(f"   腳本版本: v{scripts_version}")
    print()
    
    # 建立 manifest 結構
    manifest = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "components": {}
    }
    
    # 檢查核心程式檔案
    core_file = DIST_DIR / f"AutoFlow_Core_v{core_version}.zip"
    if core_file.exists():
        print(f"✅ 找到核心程式: {core_file.name}")
        manifest["components"]["core"] = {
            "version": core_version,
            "file": core_file.name,
            "size": get_file_size(core_file),
            "sha256": calculate_sha256(core_file),
            "download_url": f"https://github.com/{REPO_NAME}/releases/download/v{version}/{core_file.name}"
        }
        print(f"   大小: {manifest['components']['core']['size'] / 1024 / 1024:.2f} MB")
        print(f"   SHA256: {manifest['components']['core']['sha256'][:16]}...")
    else:
        print(f"⚠️  未找到核心程式檔案: {core_file}")
        print(f"   將使用上一版本的核心")
    
    print()
    
    # 檢查外部腳本檔案
    scripts_file = DIST_DIR / f"Scripts_v{scripts_version}.zip"
    if scripts_file.exists():
        print(f"✅ 找到外部腳本: {scripts_file.name}")
        manifest["components"]["scripts"] = {
            "version": scripts_version,
            "file": scripts_file.name,
            "size": get_file_size(scripts_file),
            "sha256": calculate_sha256(scripts_file),
            "download_url": f"https://github.com/{REPO_NAME}/releases/download/v{version}/{scripts_file.name}"
        }
        print(f"   大小: {manifest['components']['scripts']['size'] / 1024 / 1024:.2f} MB")
        print(f"   SHA256: {manifest['components']['scripts']['sha256'][:16]}...")
    else:
        print(f"❌ 錯誤: 未找到外部腳本檔案: {scripts_file}")
        return False
    
    print()
    
    # 讀取 CHANGELOG.md 的最新版本說明
    changelog_file = Path("CHANGELOG.md")
    if changelog_file.exists():
        changelog_text = changelog_file.read_text(encoding="utf-8")
        # 提取最新版本的更新說明 (簡化版)
        lines = changelog_text.split("\n")
        changelog_section = []
        in_current_version = False
        for line in lines:
            if f"## [v{version}]" in line or f"## v{version}" in line:
                in_current_version = True
                continue
            if in_current_version:
                if line.startswith("## "):  # 下一個版本
                    break
                changelog_section.append(line)
        
        manifest["changelog"] = "\n".join(changelog_section).strip()
    else:
        manifest["changelog"] = f"AutoFlow Control Center v{version} 發布版本"
    
    # 寫入 manifest.json
    manifest_file = DIST_DIR / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Manifest 已生成: {manifest_file}")
    print()
    print("📋 Manifest 內容:")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    
    return True


if __name__ == "__main__":
    success = generate_manifest()
    exit(0 if success else 1)
