function Test-Cred{
	[CmdletBinding()]
	[OutputType([String])]
	
	Param (
		$Username,
		$Password
	)

	Add-Type -assemblyname system.DirectoryServices.accountmanagement 
	$DS = New-Object System.DirectoryServices.AccountManagement.PrincipalContext([System.DirectoryServices.AccountManagement.ContextType]::Machine)
	
	
	If ($DS.ValidateCredentials("$($env:userdomain)\$Username",$Password))
	{
		return "$($Username) Authenticated"
	}
	Else
	{
		Write-Progress "$($Username) Not authenticated"
	}
}
