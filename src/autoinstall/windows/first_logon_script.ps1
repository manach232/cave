#Requires -RunAsAdministrator
#Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# interface config

{% for mac, ipv4, prefix_length, interface_gw, interface_dns, is_mngm_net in interfaces %}
$index = $((Get-NetAdapter | where {$_.MacAddress -eq ('{{ mac }}' -replace ":","-")}).InterfaceIndex)

{% if interface_dns %}
Set-DnsClientServerAddress -InterfaceIndex $index -ServerAddresses ('{{ interface_dns }}')
{% endif %}

New-NetIPAddress -InterfaceIndex "$index" -IPAddress {{ ipv4 }} -PrefixLength {{ prefix_length }} {% if interface_gw %} -DefaultGateway {{ interface_gw }} {% endif %}

{% if is_mngm_net %}
Set-NetIPInterface -InterfaceIndex "$index" -InterfaceMetric 1
{% endif %}

{% endfor %}
Clear-DnsClientCache

# wait for dns to be working in windows this takes a while
do{Resolve-DnsName -QuickTimeout github.com} while($? -ne $true)

[Net.ServicePointManager]::SecurityProtocol = "tls12, tls11"
cd "C:\Program Files"
ping github.com
Invoke-WebRequest 'https://github.com/PowerShell/Win32-OpenSSH/releases/download/v9.8.1.0p1-Preview/OpenSSH-Win64-v9.8.1.0.msi' -OutFile openssh.msi
Start-Process msiexec.exe -ArgumentList "/i ""$PWD\openssh.msi"" ADDLOCAL=Server" -Wait

netsh advfirewall firewall add rule name='allow ssh' protocol=TCP localport=22 dir=in action=allow

Set-Content -Force -Path "$env:ProgramData\ssh\administrators_authorized_keys" -Encoding UTF8 -Value '{{ ssh_pub }}'

$acl = Get-Acl C:\ProgramData\ssh\administrators_authorized_keys
$acl.SetAccessRuleProtection($true, $false)
$administratorsRule = New-Object system.security.accesscontrol.filesystemaccessrule("Administrators","FullControl","Allow")
$systemRule = New-Object system.security.accesscontrol.filesystemaccessrule("SYSTEM","FullControl","Allow")
$acl.SetAccessRule($administratorsRule)
$acl.SetAccessRule($systemRule)
$acl | Set-Acl

# add newline

Add-Content -Force -Path "$env:ProgramData\ssh\sshd_config" -Encoding UTF8 -Value ''

# end match-block, alternatively insert at beginning of file
Add-Content -Force -Path "$env:ProgramData\ssh\sshd_config" -Encoding UTF8 -Value 'Match all'

Add-Content -Force -Path "$env:ProgramData\ssh\sshd_config" -Encoding UTF8 -Value 'PasswordAuthentication no'
Add-Content -Force -Path "$env:ProgramData\ssh\sshd_config" -Encoding UTF8 -Value 'SyslogFacility LOCAL0'
Add-Content -Force -Path "$env:ProgramData\ssh\sshd_config" -Encoding UTF8 -Value 'LogLevel Debug3'

Set-Service -Name "sshd" -StartupType "Automatic"
Restart-Service -Name "sshd"

netsh advfirewall firewall add rule name='ICMP Allow incoming V4 echo request' protocol=icmpv4:8,any dir=in action=allow
