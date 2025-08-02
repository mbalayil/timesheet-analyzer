# Makefile for Timesheet Analyzer

.PHONY: all setup install run clean

all: setup install run

setup:
	python -m venv venv-timesheet
	venv-timesheet/bin/activate && \
	pip install uv

install:
	venv-timesheet/bin/activate && \
	uv sync

clean:
	rm -rf venv-timeshseet __pycache__ .ruff_cache

run:
	venv-timesheet/bin/activate && \
	uv run streamlit run main.py

check:
	venv-timesheet/bin/activate && \
	uv tool run ruff check
