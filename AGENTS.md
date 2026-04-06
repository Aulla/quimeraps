# AGENTS.md

## Repository Description

`quimera-ps` is a Python-based printing service built around a JSON-RPC server that processes JasperReports reports and fills them with data received through service calls.

The repository is organized around three main pieces:

- `server`: JSON-RPC service layer for report processing and printing workflows.
- `client`: PyQt6 desktop UI for monitoring the server and managing printers/models.
- `daemon`: installation and service-management helpers for running Quimera as a system service.

## Main Project Areas

- `/quimeraps`
  Main Python package with the runtime code.
- `/quimeraps/json_srv`
  Server-side JSON-RPC logic, daemon helpers, logging, utilities, and service entrypoints.
- `/quimeraps/client_gui`
  PyQt6 client UI files and window logic.
- `/server.py`, `/client.py`, `/daemon.py`
  Top-level launcher scripts.
- `/setup.py`
  Packaging and installation metadata.
- `/requirements.txt`
  Python dependency list.

## Operational Notes

- The project depends on Java and Ghostscript for report generation workflows described in `README`.
- Reports are expected to live outside the repo in the installation-specific `reports` directory.
- The repository includes generated/build artifacts under `/build`, `/dist`, and `*.egg-info`; prefer editing source files under `/quimeraps`.
- The server bind address is configurable through `QUIMERAPS_HOST` and `QUIMERAPS_PORT` and defaults to `0.0.0.0:4000`.

## Guidance For Future Tasks

- Check whether changes belong in source files under `/quimeraps` rather than mirrored files under `/build/lib`.
- Preserve existing packaging and entrypoint behavior unless the task explicitly requires changing installation flows.
- If service behavior is modified, consider impacts on Linux daemon usage and Windows service installation paths documented in `README`.
