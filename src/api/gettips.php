<?
/*
gettips.php

Parameters:
callback : the callback function name ("fff")
tips : comma separated list of comment ids ("c7h194m,c7h2doo,c7h1wst")

Response: Array of JSON objects that correspond to each input tip (if it exists)
fullname : fullname of the comment ("t1_c7h194m")
status : ("pending", "completed", "reversed", or "cancelled")
sender : "TheDJFC"
receiver : "drewdtom"
amountBTC : "0.01"
amoundUSD : "0.14"
tx : url to the transaction ("http:\/\/blockchain.info\/tx\/49d7e88a5434cdb8bef71ed404e235be73a15a8a3c391611c939265ad245e166")

example: http://bitcointip.net/api/gettips.php?callback=fff&tips=c7h194m,c7h2doo,c7h1wst
*/

header('content-type: application/json; charset=utf-8');

//connect to database
require('init.php');

//get variables
$tips = split(",", mysql_real_escape_string($_GET['tips']));
$callback = mysql_real_escape_string($_GET['callback']);

$returntips = array();

//go through the array of tip ids and get the relevent data on each one
foreach ($tips as $key => $value)
{
$result = mysql_query("SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE url='t1_$value'", $con);
while($row = mysql_fetch_array($result))
		{
		$fullname = $row['url'];
		$status = $row['status'];
		$sender = $row['sender_username'];
		$receiver = $row['receiver_username'];
		$amountBTC = $row['amount_BTC'];
		$amountUSD = $row['amount_USD'];
		$tx = "http://blockchain.info/tx/".$row['transaction_id'];
		
		
		array_push($returntips,array('fullname'=>$fullname, 'status'=>$status, 'sender'=>$sender, 'receiver'=>$receiver, 'amountBTC'=>$amountBTC, 'amountUSD'=>$amountUSD, 'tx'=>$tx));
		}
}

echo $callback . '('.json_encode($returntips).')';
?>