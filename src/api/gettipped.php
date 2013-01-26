<?
/*
gettipped.php

Parameters:
callback : the callback function name ("fff") (if defined returns JSONP, else returns JSON)
tipped : comma separated list of comment ids ("c7ny177,c7hxeas")

Response: Array of JSON objects that correspond to each input comment/post (if it exists)
fullname : fullname of the comment/post ("t1_c7ny177") (could be "t3_xxxxx" for a post)
tipQTY : number of contributors ("3")
amountBTC : total amount of BTC tipped ("0.01")
amountUSD : total amount of USD tipped ("0.14") (based on cost to tipper at time of tip)

JSON example: http://bitcointip.net/api/gettipped.php?tipped=c7hxeas,c7ny177
JSONP example: http://bitcointip.net/api/gettipped.php?callback=fff&tipped=c7hxeas,c7ny177
*/

header('content-type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

//connect to database
require('init.php');

//get variables
$tipped = split(",", mysql_real_escape_string($_GET['tipped']));
$callback = mysql_real_escape_string($_GET['callback']);

$returntipped = array();

//go through the array of tip ids and get the relevent data on each one
foreach ($tipped as $key => $value)
{
$result = mysql_query("SELECT * FROM TEST_TABLE_TIPPED WHERE thing_name LIKE 't%\_$value'", $con);
while($row = mysql_fetch_array($result))
		{
		$fullname = $row['thing_name'];
		$tipQTY = $row['tips_qty'];
		$amountBTC = $row['amount_BTC'];
		$amountUSD = $row['amount_USD'];
		
		array_push($returntipped, array('fullname'=>$fullname, 'tipQTY'=>intval($tipQTY), 'amountBTC'=>$amountBTC, 'amountUSD'=>$amountUSD));
		}
}

if ($callback!="")
	{
	echo $callback . '('.json_encode($returntipped).')';
	}
else
	{
	echo json_encode($returntipped);
	}
?>