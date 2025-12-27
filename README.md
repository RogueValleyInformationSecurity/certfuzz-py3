# CERT Basic Fuzzing Framework (BFF) - Python 3 Port

This is a Python 3.11+ port of the CERT Basic Fuzzing Framework (BFF).

**Original Project:** [CERTCC/certfuzz](https://github.com/CERTCC/certfuzz)

BFF for Windows was formerly known as the CERT Failure Observation Engine (FOE).

## Requirements

- **Python 3.11+** - Download from [python.org](https://www.python.org/downloads/)
- **uv** - Modern Python package manager (recommended) - Install via `pip install uv` or see [uv documentation](https://docs.astral.sh/uv/)

### Windows-Specific Requirements

- **Windows SDK Debugging Tools** - Required for crash analysis
  - Download from [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)
  - During installation, select only "Debugging Tools for Windows"
- **!exploitable extension** (msec.dll) - For crash severity analysis
  - Copy to the `winext` folder of your debugging tools installation

### Dependencies

BFF uses the following Python packages (automatically installed via uv):
- numpy >= 1.24.0
- scipy >= 1.11.0
- PyYAML >= 6.0
- pywin32 >= 306 (Windows only)
- WMI >= 1.5.1 (Windows only)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/CERTCC/certfuzz.git
cd certfuzz

# Install dependencies with uv
uv sync
```

### Running BFF

**Windows:**
```powershell
cd src\windows
uv run bff.py
```

**Linux/macOS:**
```bash
cd src/linux
uv run bff.py
```

## Getting Started with Fuzzing

This guide will help you set up your first fuzzing campaign.

### Step 1: Choose a Target Application

Select an application that processes file input. Good candidates include:
- Image viewers/converters (process PNG, JPEG, GIF, etc.)
- Document readers (process PDF, DOC, etc.)
- Media players (process MP3, MP4, etc.)
- Archive utilities (process ZIP, TAR, etc.)

### Step 2: Gather Seed Files

Collect sample input files that your target application can process:
- Use valid, well-formed files that the application handles correctly
- Include variety - different sizes, features, and formats
- Place seed files in the `seedfiles` directory

### Step 3: Configure Your Campaign

Copy and modify the example configuration file:

**Windows:** `src/windows/configs/examples/bff.yaml`
**Linux:** `src/linux/configs/bff.yaml`

Key configuration sections:

```yaml
# Campaign identification
campaign:
    id: my_first_fuzz_campaign

# Target application settings
target:
    program: C:\path\to\target.exe          # Path to target executable
    cmdline_template: $PROGRAM $SEEDFILE    # How to invoke with a test file

# Directory settings
directories:
    seedfile_dir: seedfiles\my_seeds        # Where your seed files are
    working_dir: fuzzdir                    # Temporary working directory
    results_dir: results                    # Where crash results are saved

# Runtime settings
runner:
    runtimeout: 5                           # Seconds before killing hung process

# Fuzzing strategy
fuzzer:
    fuzzer: bytemut                         # Mutation strategy (see below)
```

### Step 4: Understanding Fuzzer Options

BFF supports several mutation strategies:

| Fuzzer | Description | Best For |
|--------|-------------|----------|
| `bytemut` | Randomly replaces bytes | General-purpose fuzzing |
| `swap` | Swaps adjacent bytes | Format-sensitive targets |
| `wave` | Cycles through all byte values | Exhaustive testing |
| `drop` | Removes bytes from file | Parser testing |
| `insert` | Inserts random bytes | Buffer overflow detection |
| `truncate` | Truncates file end | EOF handling bugs |

### Step 5: Run Your Campaign

```bash
uv run bff.py
```

BFF will:
1. Load seed files from your configured directory
2. Apply mutations to create test cases
3. Run each test case against your target
4. Detect and log crashes
5. Minimize crashing test cases (optional)
6. Save unique crashes to the results directory

### Step 6: Analyze Results

Crashes are saved in your `results_dir` with:
- The crashing test case file
- Crash details and stack traces
- Exploitability assessment (via !exploitable on Windows)

Results are organized by crash signature (unique stack hash).

### Tips for Effective Fuzzing

1. **Use a RAM disk** for `working_dir` to reduce disk I/O and speed up fuzzing
2. **Start with diverse seed files** - variety leads to better coverage
3. **Set appropriate timeouts** - too short misses slow crashes, too long wastes time
4. **Enable minimization** - smaller crash files are easier to analyze
5. **Let it run** - some bugs only appear after thousands of iterations

## Project Structure

```
certfuzz/
├── src/
│   ├── certfuzz/           # Core fuzzing framework
│   │   ├── campaign/       # Campaign management
│   │   ├── fuzzers/        # Mutation strategies
│   │   ├── debuggers/      # Crash analysis
│   │   ├── minimizer/      # Test case minimization
│   │   └── ...
│   ├── windows/            # Windows-specific code
│   │   ├── bff.py          # Windows entry point
│   │   └── configs/        # Example configurations
│   └── linux/              # Linux/macOS-specific code
│       ├── bff.py          # Linux entry point
│       └── configs/        # Example configurations
└── pyproject.toml          # Python project configuration
```

## Using the Code

### Easy

The BFF code is in the `src/certfuzz` package. To use this code with an existing BFF installation, replace the `certfuzz` directory in your installation with the one from this repository.

### Moderate

Platform-specific code is in `src/windows` and `src/linux`. BFF for macOS uses `src/linux`. See the platform-specific README files for details.

### Running Tests

```bash
uv run python -m pytest src/test_certfuzz/ -v
```

Note: Some tests are platform-specific (Linux-only tools like GDB, zzuf).

## About BFF

The CERT Basic Fuzzing Framework (BFF) is a software testing tool that finds defects in applications that run on Linux, macOS, and Windows.

BFF performs mutational fuzzing on software that consumes file input. It automatically collects test cases that cause software to crash in unique ways, along with debugging information associated with the crashes. The goal of BFF is to minimize the effort required for software vendors and security researchers to efficiently discover and analyze security vulnerabilities found via fuzzing.

### Key Features

- **Minimal configuration** - Start fuzzing quickly with sensible defaults
- **Automatic recovery** - Handles common interruptions without manual intervention
- **Intelligent deduplication** - Uses backtrace analysis to identify unique crashes
- **Test case minimization** - Reduces crash files to minimal reproducing cases
- **Machine learning** - Automatically optimizes fuzzing parameters over time
- **Exploitability triage** - Assesses crash severity and potential exploitability

### Vulnerabilities Found with BFF

At CERT/CC, we have used BFF to find critical vulnerabilities in products including Adobe Reader and Flash Player, Apple QuickTime and Preview, Foxit Reader, FFmpeg, Wireshark, and many others. See [Public Vulnerabilities Discovered Using BFF](https://github.com/CERTCC/certfuzz/wiki/Public-Vulnerabilities-Discovered-Using-BFF).

## For More Information

- [CERT/CC Vulnerabilities Blog](https://insights.sei.cmu.edu/blog/topics/certcc/)
- [SEI Blog](https://insights.sei.cmu.edu/blog/)
