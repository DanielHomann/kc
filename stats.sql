Select test, status, Count(*) 
Into Outfile 'log/stat-temp/overview' 
From Test_Result 
Group by test, status 
Order by status Desc, test desc;
 
 
Select output,  status, Count(*) 
Into Outfile 'log/stat-temp/UnusualModuloLength'  
From Test_Result 
Where Test='UnusualModuloLength'
Group by output, status 
Order by status Desc, output Desc;

Select output,  status, Count(*) 
Into Outfile 'log/stat-temp/UnusualExponent' 
From Test_Result 
Where Test='UnusualExponent'  
Group by output, status;

Select output,  status, Count(*) 
Into Outfile 'log/stat-temp/DebianWeakKey' 
From Test_Result 
Where Test='DebianWeakKey'  
Group by output, status 
Order by status Desc;

Select 
	test,
	Floor(test_run/99999) as Test_Run_in_Set, 
	Floor(revoke_key/99999) as Revoke_Key_in_Set, 
	Count(*) 
Into Outfile 'log/stat-temp/Revokes-UsedModulo' 
From Revoke_Keys
Where test = 'UsedModulo'
Group by Floor(test_run/99999), Floor(revoke_key/99999);

Select 
	test,
	Floor(revoke_key/99999) as Revoke_Key_in_Set, 
	Count(*) 
Into Outfile 'log/stat-temp/Revokes-GlobalCommonGCD' 
From Revoke_Keys
Where test = 'GlobalCommonGCD'
Group by Floor(revoke_key/99999);

Select revoke_key
Into Outfile 'log/stat-temp/Revokes-GlobalCommonGCD-list' 
From Revoke_Keys
Where test = 'GlobalCommonGCD';

Select revoke_key
Into Outfile 'log/stat-temp/Revokes-UsedModulo-list' 
From Revoke_Keys
Where test = 'UsedModulo';



