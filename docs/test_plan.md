# Test Plan - Lantern - Network Toolkit

## Testing Philosophy
Since `lantern` interacts heavily with system commands and hardware (Wi-Fi), **we cannot rely on real system state** for core tests. Tests must be deterministic and run in CI/CD environments without network hardware.

## 1. Unit Tests (Parsers & Logic)
**Target**: `src/lantern/platforms/*` and `src/lantern/tools/*`

- **Approach**:
    - Use `pytest`.
    - Mock `CommandRunner.run()` to return pre-recorded stdout/stderr strings.
    - Assert that parsers correctly extract data objects from these strings.

- **Fixtures Needed (`tests/fixtures/`)**:
    - `macos_airport_info.txt`: output of airport -I
    - `macos_scutil_dns.txt`: output of scutil --dns
    - `linux_nmcli_dev_wifi.txt`: output of nmcli dev wifi
    - `linux_ip_route.txt`: output of ip route
    - `ifconfig_output.txt` or `ip_addr.txt`

## 2. Integration Tests (CLI Flow)
**Target**: `src/lantern/cli.py`

- **Approach**:
    - Use Typer's `CliRunner`.
    - Mock the `PlatformAdapter` factory to return a `MockAdapter`.
    - Run CLI commands and verify:
        - Exit codes (0 for success, 1 for errors).
        - Output format (contains expected strings or valid JSON).
        - Correct flags triggers (e.g., `--json` produces a dict).

## 3. Manual Verification Steps
Since some behavior is OS-dependent and hard to mock perfectly:

### Procedure
1.  **Install**: `pip install -e .`
2.  **Version**: `lantern --version` -> Check output.
3.  **Diagnose**: `lantern diagnose` -> Check valid IP/Gateway shown.
4.  **Wi-Fi Info**: `lantern wifi info` -> Compare with system menu bar info.
5.  **Scan Safety**:
    - Run `lantern wifi scan` -> **Expect Error/Warning**.
    - Run `lantern wifi scan --scan` -> Expect list of networks.
6.  **Signal**: `lantern wifi signal --count 3` -> Check for 3 updates and exit.
7.  **Format**: Add `--json` to any command above -> Verify valid JSON output.

## 4. CI Pipeline (Future)
- Linting: `ruff check .`
- Formatting: `ruff format --check .`
- Types: `mypy src`
- Tests: `pytest`
