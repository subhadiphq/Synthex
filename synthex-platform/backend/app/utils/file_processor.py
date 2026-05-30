"""
Synthex File Processor — v1.0
Handles ZIP, CSV, code, text, PDF files for AI analysis.
Supports: code review, data analysis, document summarization.
"""
import io
import zipfile
from pathlib import Path
from typing import Optional

ALLOWED_EXT = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".cs", ".html",
    ".css", ".json", ".yaml", ".yml", ".toml", ".txt", ".md",
    ".csv", ".xml", ".sql", ".sh", ".bat", ".env", ".dockerfile",
}

CODE_EXT = {".py",".js",".ts",".jsx",".tsx",".java",".cpp",".c",".go",".rs",
            ".php",".rb",".swift",".kt",".cs"}
WEB_EXT = {".html",".css",".jsx",".tsx"}
CONFIG_EXT = {".json",".yaml",".yml",".toml",".env"}
TEXT_EXT = {".md",".txt",".sh",".bat"}

MAX_SIZE = 10 * 1024 * 1024   # 10MB
MAX_CHARS = 50_000             # chars per file
MAX_FILES = 30                 # files per ZIP


# ── Core Processors ───────────────────────────────────────────────────────────

def process_zip(file_bytes: bytes) -> dict:
    """Extract and process a ZIP archive."""
    result = {"type": "zip", "files": [], "total_files": 0, "text_content": ""}
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            names = zf.namelist()
            result["total_files"] = len(names)
            parts = []
            for name in names[:MAX_FILES]:
                ext = Path(name).suffix.lower()
                if ext in ALLOWED_EXT and not name.endswith("/"):
                    try:
                        content = zf.read(name).decode("utf-8", errors="ignore")
                        if len(content) < MAX_CHARS:
                            result["files"].append({
                                "name": name,
                                "size": len(content),
                                "ext": ext,
                                "type": get_file_type(name),
                                "content": content[:MAX_CHARS]
                            })
                            parts.append(f"### {name}\n```{ext[1:] if ext else ''}\n{content}\n```")
                    except Exception:
                        continue
            result["text_content"] = "\n\n".join(parts[:15])
    except zipfile.BadZipFile:
        result["error"] = "Invalid ZIP file"
    return result


def process_text(file_bytes: bytes, filename: str) -> dict:
    """Process plain text / code file."""
    try:
        content = file_bytes.decode("utf-8", errors="ignore")
        ext = Path(filename).suffix.lower()
        return {
            "type": get_file_type(filename),
            "filename": filename,
            "ext": ext,
            "content": content[:MAX_CHARS],
            "size": len(content),
            "lines": content.count("\n") + 1,
        }
    except Exception as e:
        return {"type": "error", "filename": filename, "error": str(e)}


def process_csv(file_bytes: bytes, filename: str = "data.csv") -> dict:
    """Process CSV file with basic stats."""
    try:
        content = file_bytes.decode("utf-8", errors="ignore")
        lines = content.strip().split("\n")
        headers = [h.strip() for h in lines[0].split(",")] if lines else []
        return {
            "type": "csv",
            "filename": filename,
            "headers": headers,
            "columns": len(headers),
            "rows": len(lines) - 1,
            "preview": "\n".join(lines[:20]),
            "content": content[:MAX_CHARS],
        }
    except Exception as e:
        return {"type": "error", "filename": filename, "error": str(e)}


def process_file(file_bytes: bytes, filename: str) -> dict:
    """Main entry — routes to the correct processor by file type."""
    if len(file_bytes) > MAX_SIZE:
        return {"type": "error", "filename": filename, "error": "File too large (max 10MB)"}
    ext = Path(filename).suffix.lower()
    if ext == ".zip":
        return process_zip(file_bytes)
    elif ext == ".csv":
        return process_csv(file_bytes, filename)
    else:
        return process_text(file_bytes, filename)


# ── Helper Functions ──────────────────────────────────────────────────────────

def get_file_type(filename: str) -> str:
    """Categorize file by type."""
    ext = Path(filename).suffix.lower()
    if ext == ".zip":    return "zip"
    if ext == ".csv":    return "csv"
    if ext in CODE_EXT:  return "code"
    if ext in WEB_EXT:   return "web"
    if ext in CONFIG_EXT: return "config"
    if ext in TEXT_EXT:  return "text"
    return "unknown"


def process_text_file(file_bytes: bytes, filename: str) -> dict:
    """Alias for process_text — backward compatibility."""
    return process_text(file_bytes, filename)


def build_file_context(processed: dict) -> str:
    """Build AI-ready context string from processed file dict."""
    parts = []
    # For ZIP
    if processed.get("type") == "zip":
        parts.append(f"ZIP Archive — {processed.get('total_files', 0)} files total, "
                     f"{len(processed.get('files', []))} processed:")
        if processed.get("text_content"):
            parts.append(processed["text_content"])
    # For single files
    elif processed.get("content"):
        fname = processed.get("filename", "file")
        ftype = processed.get("type", "text")
        parts.append(f"File: {fname} ({ftype})")
        parts.append(processed["content"])
    # For CSV
    elif processed.get("type") == "csv":
        parts.append(f"CSV: {processed.get('filename','data.csv')} — "
                     f"{processed.get('rows',0)} rows × {processed.get('columns',0)} columns")
        parts.append(f"Headers: {', '.join(processed.get('headers', []))}")
        parts.append(processed.get("preview", ""))
    return "\n\n".join(parts)[:50_000]


def create_zip_from_files(files: dict) -> bytes:
    """Create a ZIP file from {filename: content} dict."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files.items():
            if isinstance(content, str):
                content = content.encode("utf-8")
            zf.writestr(fname, content)
    return buf.getvalue()
