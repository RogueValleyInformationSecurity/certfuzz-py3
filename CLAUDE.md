# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the CERT Basic Fuzzing Framework (BFF), a mutational fuzzing tool for finding security vulnerabilities in applications that consume file input. It runs on Linux, macOS, and Windows. The Windows version was formerly known as FOE (Failure Observation Engine).

## Repository Structure

- `src/certfuzz/` - Core Python package (cross-platform fuzzing logic)
- `src/linux/` - Linux/macOS-specific files including batch scripts and configs
- `src/windows/` - Windows-specific files, configs, and tools
- `src/test_certfuzz/` - Unit tests for the certfuzz package
- `build/` - Build system for creating release packages (internal CI use)
- `src/experimental/` - Experimental/deprecated features

## Architecture

BFF uses a layered architecture with platform-specific implementations:

**Campaign Layer** (`campaign/`)
- `CampaignBase` → `LinuxCampaign` / `WindowsCampaign`
- Manages fuzzing campaigns, seed file selection, and state persistence

**Iteration Layer** (`iteration/`)
- `IterationBase` → `LinuxIteration` / `WindowsIteration`
- Each iteration: selects seed file → fuzzes it → runs target → detects crash

**Fuzzer Layer** (`fuzzers/`)
- `Fuzzer` base class with mutation strategies: `bytemut`, `bitmut`, `swap`, `drop`, `insert`, `truncate`, `wave`, `nullmut`, `crmut`, `crlfmut`, `zzuf`
- Fuzzers mutate seed files within configurable byte ranges

**Runner Layer** (`runners/`)
- `zzufrun` (Linux) - uses zzuf for mutation and crash detection
- `winrun` (Windows XP/2003) - exception hooking without debugger
- `nullrun` (Windows) - uses cdb debugger for crash detection

**Debugger Layer** (`debuggers/`)
- `gdb` (Linux) with CERT Triage Tools for exploitability analysis
- `crashwrangler` (macOS)
- `msec` (Windows) - uses cdb with !exploitable extension

**Analyzer Layer** (`analyzers/`)
- Post-crash analysis: valgrind, callgrind, drillresults, stderr capture

**Minimizer** (`minimizer/`)
- Reduces crashing test cases to minimal byte changes from seed file
- String minimization for exploit development (Metasploit pattern support)

**Test Case** (`testcase/`)
- `TestCaseBase` → platform variants
- Captures crash metadata, exploitability, hash for uniqueness

## Running Tests

Tests are in `src/test_certfuzz/` using Python unittest:

```bash
# Run all tests
cd src
python -m pytest test_certfuzz/

# Run specific test module
python -m pytest test_certfuzz/fuzzers/test_bytemut.py

# Run with unittest directly
python -m unittest discover -s test_certfuzz -p 'test_*.py'
```

## Configuration

BFF uses YAML config files. Examples:
- Linux: `src/linux/configs/bff.yaml`
- Windows: `src/windows/configs/examples/bff.yaml`

Key config sections:
- `campaign.id` - Identifies the fuzzing campaign
- `target.program` - Path to target executable
- `target.cmdline_template` - Command line with `$PROGRAM` and `$SEEDFILE` placeholders
- `runner.runtimeout` - Max execution time per iteration
- `directories.seedfile_dir`, `working_dir`, `results_dir`

## Dependencies

- Python 2.7 (Python 3 not yet supported)
- NumPy, SciPy, PyYAML
- Platform-specific:
  - Linux: gdb 7.2+, zzuf (CERT-patched version), valgrind
  - macOS: CrashWrangler, libgmalloc
  - Windows: Debugging Tools for Windows, !exploitable (msec.dll), pywin32, WMI

## Key Entry Points

- Linux/macOS: `src/linux/batch.sh` → `bff.py`
- Windows: `bff.py` via Start menu or command line

The main loop: `BFF` class (`bff/common.py`) instantiates a `Campaign` which runs `Iteration`s. Each iteration uses a `Fuzzer` to mutate a seed file, a `Runner` to execute the target, and on crash, creates a `TestCase` for analysis and minimization.
