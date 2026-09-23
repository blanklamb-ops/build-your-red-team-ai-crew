#!/bin/sh
set -u

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
archive_dir="$project_dir/scanner-output"
mkdir -p "$archive_dir"

timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

if command -v semgrep >/dev/null 2>&1; then
    {
        echo "scanner=semgrep"
        echo "timestamp=$timestamp"
        echo "command=semgrep scan --metrics=off --disable-version-check --no-git-ignore --config config/semgrep.yml after_action scripts tests"
        cd "$project_dir" && SEMGREP_SETTINGS_FILE="$archive_dir/.semgrep-settings.yml" SEMGREP_LOG_FILE="$archive_dir/.semgrep.log" semgrep scan --metrics=off --disable-version-check --no-git-ignore --config config/semgrep.yml after_action scripts tests
        status=$?
        echo "exit_status=$status"
    } >"$archive_dir/semgrep.txt" 2>&1
else
    {
        echo "scanner=semgrep"
        echo "timestamp=$timestamp"
        echo "command=semgrep scan --metrics=off --disable-version-check --no-git-ignore --config config/semgrep.yml after_action scripts tests"
        echo "status=NOT_AVAILABLE"
    } >"$archive_dir/semgrep.txt"
fi

if command -v ast-grep >/dev/null 2>&1; then
    {
        echo "scanner=ast-grep"
        echo "timestamp=$timestamp"
        echo "command=ast-grep --pattern eval(\$A) --lang python after_action"
        cd "$project_dir" && ast-grep --pattern 'eval($A)' --lang python after_action
        status=$?
        echo "exit_status=$status"
    } >"$archive_dir/ast-grep.txt" 2>&1
else
    {
        echo "scanner=ast-grep"
        echo "timestamp=$timestamp"
        echo "command=ast-grep --pattern eval(\$A) --lang python after_action"
        echo "status=NOT_AVAILABLE"
    } >"$archive_dir/ast-grep.txt"
fi
