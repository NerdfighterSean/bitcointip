<?
/*
/api/balance.php

Parameters:
"username" : reddit username
"address" : bitcoin address associated with user "username"

Response: 
"username" : reddit username 
"address" : bitcoin address associated with user "username"
"balanceBTC" : the BTC balance of "address"
"balanceUSD" : the USD balance of "address"
"balanceAUD" : the AUD balance of "address"
"balanceCAD" : the CAD balance of "address"
"balanceJPY" : the JPY balance of "address"
"balanceGBP" : the GBP balance of "address"
"balanceEUR" : the EUR balance of "address"

If the given address does not belong to the given user, an empty array will be returned.
*/

header('content-type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

//have the user keep their balance cached for an hour.
$expirationage = 60*60*1;
$expirationdate = time()+$expirationage;
Header("Cache-Control: max-age=".$expirationage." must-revalidate");
Header("Expires: " . gmdate("D, d M Y H:i:s", $expirationdate) . " GMT");

//connect to database
require('init.php');

//get parameters
$username = mysql_real_escape_string($_GET['username']);
$address = mysql_real_escape_string($_GET['address']);

$returnpackage = array();

//get current exchange rate
$result = mysql_query("SELECT * FROM TEST_TABLE_RECENT WHERE type='lastexchangeratefetched'", $con);
while($row = mysql_fetch_array($result))
		{
		$rates = json_decode($row['timestamp'], true);
		}

//get balanceBTC
$result = mysql_query("SELECT * FROM TEST_TABLE_USERS WHERE username='$username' AND address='$address'", $con);
while($row = mysql_fetch_array($result))
		{
		$balanceBTC = round($row['balance'],8);
		$username = $row['username'];
		$address = $row['address'];
		$balanceUSD = round($balanceBTC*$rates['USD'],2);
		$balanceAUD = round($balanceBTC*$rates['AUD'],2);
		$balanceCAD = round($balanceBTC*$rates['CAD'],2);
		$balanceJPY = round($balanceBTC*$rates['JPY'],0);
		$balanceGBP = round($balanceBTC*$rates['GBP'],2);
		$balanceEUR = round($balanceBTC*$rates['EUR'],2);

		$returnpackage = array('username'=>$username, 'address'=>$address, 'balanceBTC'=>$balanceBTC, 'balanceUSD'=>$balanceUSD, 'balanceAUD'=>$balanceAUD, 'balanceCAD'=>$balanceCAD, 'balanceJPY'=>$balanceJPY, 'balanceGBP'=>$balanceGBP, 'balanceEUR'=>$balanceEUR);
		}
		
echo json_encode($returnpackage);

?>