@echo off
call .venv\Scripts\activate
python src\ingestion\pipeline.py
pause