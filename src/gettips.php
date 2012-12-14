<?php header('content-type: application/json; charset=utf-8');

//connect to database with init.php
require (init.php);

//http://example.com/gettips.php?callback=callback&comment_names[]=name1&comment_names[]=name2&comment_names[]=name3
$comment_names = $_GET['comment_names'];

//go through the array of comment_names and get the relevent data on each comment
foreach ($comment_names as $value)
	{
	$result = mysql_query("SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE url='$value'", $con);
	while($row = mysql_fetch_array($result))
  		{
			$status = $row['status']; //completed, pending, reversed, cancelled
			$sender = $row['sender_username']; 
			$receiver = $row['receiver_username']; 
			$amountBTC = $row['amount_BTC']; 
			$amountUSD = $row['amount_USD'];
			$tx = "http://blockchain.info/tx/".$row['txid'];
			
			$tips[$value] = array('status'=>$status, 'sender'=>$sender, 'receiver'=>$receiver, 'amountBTC'=>$amountBTC, 'amoundUSD'=>$amountUSD, 'tx'=>$tx);
		}
	}

echo $_GET['callback'] . '('.json_encode($tips).')';

?>
