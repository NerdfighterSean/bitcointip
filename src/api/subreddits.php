<?
/*
api/subreddits.php

Response: 
"subreddits": A list of "subreddits" that are enabled.
*/


header('content-type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

//Have the user keep the subreddit list cached for a day.
$expirationage = 60*60*24*1;
$expirationdate = time()+$expirationage;
Header("Cache-Control: max-age=".$expirationage." must-revalidate");
Header("Expires: " . gmdate("D, d M Y H:i:s", $expirationdate) . " GMT");

//connect to database
require('init.php');

$returnpackage = array();
$subreddits = array();

//create the list of subreddits
$result = mysql_query("SELECT * FROM TEST_TABLE_ENABLED_SUBREDDITS WHERE 1 ORDER BY subreddit ASC", $con);
while($row = mysql_fetch_array($result))
		{
		$subreddit = strtolower($row['subreddit']);
		array_push($subreddits, $subreddit);
		}

$returnpackage['subreddits'] = $subreddits;

echo json_encode($returnpackage);

?>