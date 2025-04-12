from fastapi import APIRouter, UploadFile, File, HTTPException
from src.analysis.ast_analyzer import CodeAnalyzer
from src.llm.llm_fixer import get_ai_fix_local
from src.analysis.report_generator import save_report
import time
import re

router = APIRouter()

# ✅ Normalize description by removing tags like [unused_variable]
def normalize_description(desc: str):
    return re.sub(r"\[.*?\]$", "", desc.strip())

@router.get("/")
async def home():
    return {"message": "Welcome to AI Code Reviewer! Visit /docs for API usage."}


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    """Upload a Python file & analyze it."""
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python (.py) files are allowed.")

    content = await file.read()
    code = content.decode("utf-8")
    lines = code.splitlines()

    analyzer = CodeAnalyzer()
    raw_issues = analyzer.analyze_code(code)

    # ✅ Final deduplication using (line, normalized desc or tag)
    seen = set()
    issues = []
    for issue in raw_issues:
        line = issue[0]
        raw_desc = issue[1]
        tag = issue[2] if len(issue) == 3 else None

        desc = normalize_description(raw_desc)
        key = (line, tag or desc)

        if key not in seen:
            seen.add(key)
            issues.append((line, desc, tag) if tag else (line, desc))

    results = []

    for issue in issues:
        if len(issue) == 3:
            line, desc, issue_type = issue
        elif len(issue) == 2:
            line, desc = issue
            issue_type = None
        else:
            continue  # skip malformed

        print(f"⏱️ Starting fix for line {line} - {desc}")
        start_time = time.time()

        fix = get_ai_fix_local(code, desc, issue_line=line, issue_type=issue_type)

        elapsed = time.time() - start_time
        print(f"✅ Fix for line {line} took {elapsed:.2f} seconds")

        preview_start = max(line - 2, 0)
        preview_end = min(line + 1, len(lines))
        code_preview = "\n".join(lines[preview_start:preview_end])

        results.append({
            "line": line,
            "issue": desc,
            "fix": fix,
            "preview": code_preview,
            "issue_type": issue_type
        })

    save_report(file.filename, results)
    return {"filename": file.filename, "issues": results}
