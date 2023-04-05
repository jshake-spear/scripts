:: This script is used to disable Windows firewall rules for vulnerable services that are open by default.
:: File must be run with administrator privileges
netsh advfirewall firewall set rule group="Remote Administration" new enable=no
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=no
powershell.exe -command " & {Get-NetFirewallPortFilter | Where-Object { $_.LocalPort -eq 135 -or $_.LocalPort -eq 137 -or $_.LocalPort -eq 138 -or $_.LocalPort -eq 139 } | get-netfirewallrule | Where-Object { $_.Group } | Disable-NetFirewallRule }"
