param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CommandArgs
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$cliPath = Join-Path $PSScriptRoot "bharattrader-ai\cli.py"
python $cliPath @CommandArgs
