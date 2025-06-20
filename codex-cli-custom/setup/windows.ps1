Param(
  [string]$NodeVersion = "22",
  [string]$PnpmVersion = "latest"
)

Write-Host "`n> Installing Node $NodeVersion with Volta"
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://get.volta.sh'))

$env:PATH = "$HOME\.volta\bin;$env:PATH"
volta install "node@$NodeVersion"

Write-Host "> Enabling Corepack + pnpm $PnpmVersion"
corepack enable
corepack prepare "pnpm@$PnpmVersion" --activate

Write-Host "> Restoring dependencies"
pnpm install --frozen-lockfile

Write-Host "> Bootstrapping Husky hooks"
pnpm exec husky install