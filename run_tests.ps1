# Run all tests
# Usage:
#   .\run_tests.ps1              # all tests
#   .\run_tests.ps1 domain       # only domain tests
#   .\run_tests.ps1 application  # only application tests
#   .\run_tests.ps1 infrastructure # only infrastructure tests

$filter = $args[0]

if ($filter) {
    .\.venv\Scripts\python.exe -m pytest tests/unit/$filter -v
} else {
    .\.venv\Scripts\python.exe -m pytest -v
}
