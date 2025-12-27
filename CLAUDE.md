# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Python 3.11+ port** of the CERT Basic Fuzzing Framework (BFF), a mutational fuzzing tool for finding security vulnerabilities in applications that consume file input. It runs on Linux, macOS, and Windows.

**Original Project:** https://github.com/CERTCC/certfuzz

The Windows version was formerly known as FOE (Failure Observation Engine).

## Repository Structure

- `src/certfuzz/` - Core Python package (cross-platform fuzzing logic)
- `src/linux/` - Linux/macOS-specific files including batch scripts and configs
- `src/windows/` - Windows-specific files, configs, and tools
- `src/test_certfuzz/` - Unit tests for the certfuzz package
- `build/` - Build system for creating release packages (internal CI use)
- `src/experimental/` - Experimental/deprecated features
- `pyproject.toml` - Python project configuration for uv/pip

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
- `nullrun` (Windows Vista+) - uses cdb debugger for crash detection

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

## Running BFF

```bash
# Install dependencies
uv sync

# Run on Windows
cd src/windows
uv run bff.py

# Run on Linux/macOS
cd src/linux
uv run bff.py
```

## Running Tests

```bash
# Run all tests with pytest
uv run python -m pytest src/test_certfuzz/ -v

# Run specific test module
uv run python -m pytest src/test_certfuzz/fuzzers/test_bytemut.py

# Quick summary
uv run python -m pytest src/test_certfuzz/ -q
```

**Note:** Some tests are platform-specific:
- `test_gdb*.py`, `test_zzuf*.py` - Linux only (require GDB, zzuf)
- `test_minimizer_base.py` - May have Windows file locking issues in tearDown

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
- `fuzzer.fuzzer` - Mutation strategy (bytemut, swap, wave, drop, insert, truncate)

## Dependencies

**Python:** 3.11+ (migrated from Python 2.7)

**Package Manager:** uv (recommended) or pip

**Python Packages** (see pyproject.toml):
- numpy >= 1.24.0
- scipy >= 1.11.0 (replaces hcluster for clustering)
- PyYAML >= 6.0
- pywin32 >= 306 (Windows only)
- WMI >= 1.5.1 (Windows only)

**Platform-specific:**
- Linux: gdb 7.2+, zzuf (CERT-patched version), valgrind
- macOS: CrashWrangler, libgmalloc
- Windows: Debugging Tools for Windows (Windows SDK), !exploitable (msec.dll)

## Key Entry Points

- Linux/macOS: `src/linux/bff.py`
- Windows: `src/windows/bff.py`

The main loop: `BFF` class (`bff/common.py`) instantiates a `Campaign` which runs `Iteration`s. Each iteration uses a `Fuzzer` to mutate a seed file, a `Runner` to execute the target, and on crash, creates a `TestCase` for analysis and minimization.

## Python 3 Migration Notes

This port from Python 2.7 to Python 3.11+ included:

1. **Syntax updates** (via 2to3):
   - `print` statements → `print()` functions
   - `dict.iteritems()` → `dict.items()`
   - `xrange()` → `range()`
   - Exception syntax updates

2. **Bytes/string handling**:
   - `os.write()` requires bytes
   - `hashlib` functions require bytes
   - `bytearray()` constructor changes
   - File modes: use `'rb'`/`'wb'` for binary, `'r'`/`'w'` for text

3. **Library updates**:
   - `hcluster` → `scipy.cluster.hierarchy`
   - `cPickle` → `pickle`
   - `StringIO` → `io.StringIO`/`io.BytesIO`
   - `_winreg` → `winreg`

4. **Removed features**:
   - `random.jumpahead()` - replaced with hash-based seed combining
   - Tuple unpacking in lambdas

5. **Metaclass syntax**:
   - `__metaclass__ = abc.ABCMeta` → `class Foo(metaclass=abc.ABCMeta)`

## Common Development Tasks

**Adding a new fuzzer:**
1. Create class in `src/certfuzz/fuzzers/` inheriting from `Fuzzer` or `MinimizableFuzzer`
2. Implement `_fuzz()` method that reads `self.input` and writes to `self.output`
3. Register in fuzzer factory

**Debugging a crash:**
1. Check `results_dir` for crash artifacts
2. Use `src/certfuzz/tools/*/repro.py` to reproduce crashes
3. Examine `.msec` (Windows) or `.gdb` (Linux) files for exploitability

**Testing changes:**
```bash
# Run affected test module
uv run python -m pytest src/test_certfuzz/fuzzers/test_bytemut.py -v

# Run with coverage
uv run python -m pytest src/test_certfuzz/ --cov=src/certfuzz
```
