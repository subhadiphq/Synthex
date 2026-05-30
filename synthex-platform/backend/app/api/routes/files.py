"""
POST /v1/files/upload — File Intelligence Endpoint
Analyze ZIP, code, CSV, text files with AI agents.
Supports: code review, data analysis, project summarization.
"""
import io
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.database import APIKey
from app.api.middleware.auth import require_api_key
from app.database import get_db
from app.utils.file_processor import (
    process_file, process_text_file, create_zip_from_files,
    build_file_context, get_file_type
)
from app.core.pipeline import pipeline
from app.models.request import Message
from app.services.key_service import key_service

router = APIRouter()
MAX_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    model: str = Form(default="synthex-nova-forge"),
    instruction: str = Form(default="Analyze this file and provide detailed insights"),
    key: APIKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload any file for AI analysis.
    - ZIP: extracts and reviews all code files
    - Python/JS/etc: code review and improvement suggestions
    - CSV: statistical analysis and data insights
    - Markdown/txt: summarization and key points
    """
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(413, "File too large. Maximum 10MB allowed.")

    filename = file.filename or "uploaded_file"
    ftype = get_file_type(filename)  # Fixed: no content_type arg

    # Process file
    processed = process_file(content, filename)
    if processed.get("error"):
        raise HTTPException(400, f"File processing error: {processed['error']}")

    # Build context
    file_context = build_file_context(processed)

    # Summary
    if ftype == "zip":
        n_files = processed.get("total_files", 0)
        summary = f"ZIP archive — {n_files} files total"
    elif ftype == "csv":
        rows = processed.get("rows", 0)
        cols = processed.get("columns", 0)
        summary = f"CSV dataset — {rows} rows × {cols} columns"
    else:
        lines = processed.get("lines", 0)
        summary = f"{ftype} file: {filename} ({lines} lines)"

    # Build AI prompt
    messages = [Message(
        role="user",
        content=f"{instruction}\n\n[Uploaded: {summary}]\n\n{file_context[:6000]}"
    )]

    # Run pipeline
    result = await pipeline.run(
        messages=messages,
        model_id=model,
        max_tokens=2000,
        temperature=0.3,
        api_key_id=str(key.id),
    )

    # Record usage
    await key_service.record_usage(
        db=db, key_obj=key, model=model,
        provider=result.provider_used,
        input_tokens=result.total_input_tokens,
        output_tokens=result.total_output_tokens,
        cost_usd=result.total_cost_usd,
        latency_ms=result.latency_ms,
        agents_used=result.agents_used,
        success=True,
    )
    await db.commit()

    return {
        "filename": filename,
        "file_type": ftype,
        "summary": summary,
        "analysis": result.final_response,
        "agents_used": result.agents_used,
        "model_used": model,
        "tokens_used": result.total_input_tokens + result.total_output_tokens,
        "cost_usd": round(result.total_cost_usd, 6),
    }


@router.post("/files/create-zip")
async def create_zip(
    files: dict,
    key: APIKey = Depends(require_api_key),
):
    """Create ZIP from {filename: content} dict and return as download."""
    if not files:
        raise HTTPException(400, "No files provided")
    zip_bytes = create_zip_from_files(files)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=synthex-output.zip"}
    )
