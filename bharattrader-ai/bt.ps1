param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CommandArgs
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$scriptPath = Join-Path $PSScriptRoot "cli.py"
python $scriptPath @CommandArgs
