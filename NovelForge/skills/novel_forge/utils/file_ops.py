"""
文件操作工具
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


def ensure_dir(path: Path) -> Path:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file(path: Path, encoding: str = 'utf-8') -> str:
    """读取文件"""
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def write_file(path: Path, content: str, encoding: str = 'utf-8'):
    """写入文件"""
    ensure_dir(path.parent)
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)


def read_chapter(project_path: Path, chapter_num: int, volume_num: int = 1) -> Optional[str]:
    """读取章节"""
    ch_path = project_path / f"volumes/volume_{volume_num}/chapters/ch_{chapter_num:03d}.md"
    
    if ch_path.exists():
        return read_file(ch_path)
    
    return None


def write_chapter(
    project_path: Path,
    chapter_num: int,
    content: str,
    title: str = "",
    volume_num: int = 1
):
    """写入章节"""
    ch_dir = project_path / f"volumes/volume_{volume_num}/chapters"
    ensure_dir(ch_dir)
    
    ch_path = ch_dir / f"ch_{chapter_num:03d}.md"
    
    full_content = f"# {title}\n\n{content}" if title else content
    write_file(ch_path, full_content)


def list_chapters(project_path: Path, volume_num: int = 1) -> List[int]:
    """列出章节"""
    ch_dir = project_path / f"volumes/volume_{volume_num}/chapters"
    
    if not ch_dir.exists():
        return []
    
    chapters = []
    for f in ch_dir.glob("ch_*.md"):
        try:
            num = int(f.stem.split("_")[1])
            chapters.append(num)
        except (ValueError, IndexError):
            pass
    
    return sorted(chapters)


def read_json(path: Path) -> Dict[str, Any]:
    """读取JSON"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any], indent: int = 2):
    """写入JSON"""
    ensure_dir(path.parent)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def count_words(text: str) -> int:
    """统计字数"""
    import re
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words


def count_chapters_words(project_path: Path, volume_num: int = 1) -> Dict[str, Any]:
    """统计章节字数"""
    chapters = list_chapters(project_path, volume_num)
    
    total_words = 0
    chapter_words = {}
    
    for ch_num in chapters:
        content = read_chapter(project_path, ch_num, volume_num)
        if content:
            words = count_words(content)
            chapter_words[ch_num] = words
            total_words += words
    
    return {
        "total_chapters": len(chapters),
        "total_words": total_words,
        "avg_words": total_words // len(chapters) if chapters else 0,
        "chapter_words": chapter_words
    }


def backup_file(path: Path):
    """备份文件"""
    import shutil
    if path.exists():
        backup_path = Path(str(path) + '.bak')
        shutil.copy(path, backup_path)


def restore_backup(path: Path) -> bool:
    """恢复备份"""
    backup_path = Path(str(path) + '.bak')
    if backup_path.exists():
        import shutil
        shutil.copy(backup_path, path)
        backup_path.unlink()
        return True
    return False
