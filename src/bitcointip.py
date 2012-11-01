
#import reddit praw stuff
#import encryption/decryption stuff


import bitcoind
#bitcoindwrapper and custom methods
#txid = bitcoind.transact(fromthing,tothing,amount)

from time import time
#import time to get current timestamp
#timestamp = time.time()

import MySQLdb
#import mysql stuff

import urllib2
#datastring = urllib2.urlopen(url).read()

import json
#encode/decode json
#jsonarray = json.loads(jsonstring)
#jsonstring = json.dumps(jsonarray)

import re
#regex stuff


######################################################################
#MYSQL_TABLES
######################################################################


#TEST_TABLE_FACET_PAYOUTS

#TEST_TABLE_RECENT (keep track of date that users are last active for transaction reversal purposes)
	#0 type
	#1 timestamp
	
#TEST_TABLE_TOSUBMIT (comments or messages for /u/bitcointip to send)
	#0 tosubmit_id (not used)
	#1 type
	#2 replyto
	#3 subject
	#4 text
	#5 captchaid
	#6 captchasol
	#7 sent
	#8 timestamp
	
#TEST_TABLE_TRANSACTIONS
	#0  transaction_id
	#1  sender_username
	#2  sender_address
	#3  receiver_username
	#4  receiver_address
	#5  amount_BTC
	#6  amount_USD
	#7  type
	#8  url
	#9  subreddit
	#10 timestamp
	#11 verify
	#12 statusmessage
	#13 status
	
#TEST_TABLE_USERS
	#0 userid (not used)
	#1 username
	#2 address
	#3 balance (not used)
	#4 datejoined
	#5 giftamount
	

######################################################################
#SETTINGS AND OPTIONS
######################################################################

# ENCRYPTED DETAILS:
encMYSQLDBhost = "???"
encMYSQLDBlogin = "???"
encMYSQLDBpass = "???"
encMYSQLDBdbname = "??"
encBITCOINDlogin = "???"
encBITCOINDpass = "???"
encBITCOINDip = "???"
encBITCOINDport = "???"
encBITCOINDsecondpass = "???"
encREDDITbotusername = "???"
encREDDITbotpassword = "???"
encREDDITbotid = "???"

#DECRYPTION KEY
decryptionkey = "??????????"

# VARIABLES AND OPTIONS

# ALLOWED SUBREDDITS
allowedsubreddits = array("bitcointip", "test", "bitcoin", "girlsgonebitcoin", "bitmarket", "bitcoinmining", "decrypto", "mtred", "mtgox", "bitcoinmagazine")

# BANNED USERS
bannedusers = array("")

# BOTSTATUS (DOWN/UP)
botstatus = "down"

#INIT Exchange rate
exchangerate = 0
exchangeratelastupdated=0

#Timings to do things
#update exchange rate from the charts every 3 hours
updateexchangerateinterval = 60*60*3

#update transactions (pending->completed or pending->cancelled) every 24 hours
updatetransactionsinterval = 60*60*24*1

#update transactions (pending->cancelled) when transactions are 21 days old
canceltransactionsinterval = 60*60*24*21

#notify users that they have a pending transaction for them every 7 days.
notifytransactionsinterval = 60*60*24*7






######################################################################
#FUNCTIONS
######################################################################


# GET THE EXCHANGE RATE FROM bitcoincharts.com
def getExchangeRate(symbol):

	#if exchangeratetime is less than 3 hours ago, return the rate
	if ( ((time.time() - exchangeratelastupdated)<(updateexchangerateinterval)) ):
		return exchangerate;

	#else if the timestamp is over 3 hours old, update the exchangerate
	else:
		jsonurl = "http://bitcoincharts.com/t/markets.json"
		jsonstring = urllib2.urlopen(jsonurl).read()
		jsonarray = json.loads(jsonstring) 

		for (i, item) in enumerate(jsonarray):
			if (jsonarray[i]['symbol'] == symbol):
				exchangerate = jsonarray[i]['close']
				exchangerate = round(exchangerate,2)
				exchangeratelastupdated = time()
				return exchangerate
				
				
				

#subredditcheck
#if subreddit is in list of allowedsubreddits, return 1.
def checksubreddit(subreddit):
	
	for (i, item) in enumerate(allowedsubreddits):
		if (item.lower() == subreddit.lower()):
			#subreddit allowed
			return 1

	#subreddit not allowed
	return 0

#checkuser
#if a user is not in list of banned users, return 1.
def checkuser(username):

	for (i, item) in enumerate(bannedusers):
		if (item.lower() == username.lower()):
			#user not allowed
			return 0

	#user allowed
	return 1

#adduser	
#add a user to the service and set them up with an address and account. returns "error" if unsuccessful.
def adduser(username):
	
	#create a deposit address for them
	newuseraddress = bitcoind.getnewaddress(username);
	if (newuseraddress == "error"):
		return "error"
	else:
		#add them to TABLE_USERS
		sql = "INSERT INTO TEST_TABLE_USERS (user_id, username, address, balance, datejoined) VALUES ('%s', '%s', '%s', '%f', '%d')" % ('', username, newuseraddress, 0.00000000, time())
		mysqlcursor.execute(sql)
		mysqlcon.commit()



#update_lastactive
#update the user's lastactive time
def update_lastactive(username)

	#check if user has been active at all.  If so, update, if not insert.
	#$result = mysql_query("SELECT * FROM TEST_TABLE_RECENT WHERE type='LASTACTIVE_$username'",$con); #todo
	userhasbeenactive = 0
	
	sql = "SELECT * FROM TEST_TABLE_RECENT WHERE type='LASTACTIVE_%s'" % (username)
	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		userhasbeenactive=1
	
	
	if (userhasbeenactive == 1):
		#update username's lastactive time
		sql = "UPDATE TEST_TABLE_RECENT SET timestamp='%d' WHERE type='LASTACTIVE_%s'" % ( time.time(), username)
		mysqlcursor.execute(sql)
		mysqlcon.commit()
	else
		#insert username's lastactive time
		sql = "INSERT INTO TEST_TABLE_RECENT (type, timestamp) VALUES ('LASTACTIVE_%s', '%d')" % (username, time.time())
		mysqlcursor.execute(sql)
		mysqlcon.commit()


#getuserbalance
#Get the current balance of a user. returns "error" if unsuccessful
def getuserbalance(username):

	userbalance = bitcoind.getbalance(username)
	
	if (userbalance != "error"):
		return userbalance
	else: 
		if (adduser(username) == "error"):
			return "error"	
	
	return getuserbalance(username)

#getuseraddress
#Get the current address of a user. returns "error" if unsuccessful
def getuseraddress(username):

	useraddress = bitcoind.getaddressesbyaccount(username)[0]

	if (useraddress != "error"):
		return useraddress
	else: 
		if (adduser(username) == "error"):
			return "error"	
	
	return getuseraddress(username)




#getusergiftamount
#getusergiftamount($username) get how much the user has donated to /u/bitcointip
def getusergiftamount(username):

	$sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='%s'" % (username)

	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		giftamount = row[5]
		return giftamount

	#if nothing was returned, the user doesn't exist yet. Add them. and try again.
	if (adduser(username) == "error"):
		return "error"
	
	return getusergiftamount(username)



#userhasredeemedkarma
#checks to see if a user has gotten bitcoins from the reddit bitcoin faucet yet.
def userhasredeemedkarma(username):

	sql = "SELECT * FROM TEST_TABLE_FAUCET_PAYOUTS WHERE username='%s'" % (username)
	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		alreadyredeemed = 1
		
		
	
	if (alreadyredeemed == 1):
		print "user has redeemed karma already."
		return 1
	else:
		print "user has not redeemed karma yet.";
		return 0


#doestransactionexist
#double checks whether or not a transaction has already been done.
def doestransactionexist(sender, reciever, timestamp):

	sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE sender_username='%s' AND receiver_username='%s' AND timestamp='%d'" % (sender, receiver, timestamp)
	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		#transaction already processed
		return 1
	
	#transaction doesn't exist.
	return 0

	
#dotransaction
#do the transaction
def dotransaction(senderusername, senderaddress, receiverusername, receiveraddress, bitcoinamount, dollaramount, type, url, timestamp, subreddit, verify, status, statusmessage):

	#returns success message or failure reason
	
	print "doing transaction"	
	
	#Search for transaction in transaction list to prevent double processing!
	if ( doestransactionexist(senderusername, receiverusername, timestamp) == 1):
		print "Transaction does already exist."
		return "cancelled"

	#submit the transaction to the wallet.
	statusmessage = bitcoind.transact(senderusername, receiveraddress, bitcoinamount)
	
	print "statusmessage: statusmessage"
	
	#based on the statusmessage, set the status and process.
	if (statusmessage != "error"):
		status = "pending";
		
		if (receiverusername == ""):
			#we are sending to an address (not reversable)
			status = "completed"
	
		
		#do a transaction from sender to reciever for amount. put into TABLE_TRANSACTIONS
		sql = "INSERT INTO TEST_TABLE_TRANSACTIONS (transaction_id, sender_username, sender_address, receiver_username, receiver_address, amount_BTC, amount_USD, type, url, subreddit, timestamp, verify, statusmessage, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (statusmessage, senderusername, senderaddress, receiverusername, receiveraddress, bitcoinamount, dollaramount, type, url, subreddit, timestamp, verify, statusmessage, status)
		mysqlcursor.execute(sql)
		mysqlcon.commit()
	
	
	#if tip is to bitcointip, add tip to giftamount for $sender.
		if ( receiverusername.lower() == "bitcointip" ):
			oldgiftamount = getusergiftamount(senderusername)
			newgiftamount = oldgiftamount + bitcoinamount
			sql = "UPDATE TEST_TABLE_USERS SET giftamount='%d' WHERE username='%s'" % (newgiftamount, senderusername)
			mysqlcursor.execute(sql)
			mysqlcon.commit()
			
			#make all transactions to 'bitcointip' completed
			sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE receiver_username='bitcointip'" 
			mysqlcursor.execute(sql)
			mysqlcon.commit()
		
		print "Transaction Successful"
		
	else
		#(statusmessage == "error") the transaction didn't go through right. and is canceled
		
		status = "cancelled"
		
		#even though canceled, enter into transaction list but as cancelled
		sql = "INSERT INTO TEST_TABLE_TRANSACTIONS (transaction_id, sender_username, sender_address, receiver_username, receiver_address, amount_BTC, amount_USD, type, url, subreddit, timestamp, verify, statusmessage, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (statusmessage, senderusername, senderaddress, receiverusername, receiveraddress, bitcoinamount, dollaramount, type, url, subreddit, timestamp, verify, statusmessage, status)
		mysqlcursor.execute(sql)
		mysqlcon.commit()
	
	#cancelled or pending
	
	#update lastactive for the sender
	update_lastactive(senderusername)
	
	return status

	
	

#update_transactions
#updates pending transactions to completed or reversed depending on receiver activity
def update_transactions():

	
	##get TRANSACTIONS_UPDATED timestamp from TEST_TABLE_RECENT
	sql = "SELECT * FROM TEST_TABLE_RECENT WHERE type='TRANSACTIONS_UPDATED'"
	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		lasttransactionsupdatedtimestamp = row[1]

	
	
	print "<br>Last Update Time: lasttransactionsupdatedtimestamp"
		
		
	##do this once every day
	##if (transactiontime + 21days)< receiverlastactive, process the reversal of the transaction to the senders new address, and set transactionstatus=reversed.

	if ((lasttransactionsupdatedtimestamp+(updatetransactionsinterval)) <= time.time())
		##if the transactions haven't been updated in 1 day, do the update.
	
		$sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE status='pending'"

		mysqlcursor.execute(sql)
		results = mysqlcursor.fetchall()
		for row in results:
			transactionid = row[0]
			receiver = row[3]
			sender = row[1]
			timestamp = row[10]
			transactionamount = row[?]
			
			#get receiver lastactive time
			sql = "SELECT timestamp FROM TEST_TABLE_RECENT WHERE type='LASTACTIVE_%s'" % (receiver)
			mysqlcursor.execute(sql)
			resultsb = mysqlcursor.fetchall()
			for row in resultsb:
				receiverlastactive = row[1]
			if (receiverlastactive > timestamp):
				#mark transaction as completed because user has been active after transaction
				sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s" % (transactionid)
				mysqlcursor.execute(sql)
				mysqlcon.commit()
			else if ( (time.time()) > (timestamp + canceltransactionsinterval) and timestamp > receiverlastactive):
				#transaction is older than 21 days and pending...mark as cancelled.
				##check to make sure the reciever has enough
				receiverbalance = getuserbalance(receiver)
				if (receiverbalance >= (transactionamount))
					##the receiver has enough, just move the coins from the receiveraddress back to the new senderaddress
					newsenderaddress = bitcoind.getuseraddress(sender)
					reversalamount = transactionamount-0.0005
					
					reversalstatus = bitcoind.transact(receiveraddress, newsenderaddress, reversalamount);
					
					##mark the transaction as reversed in the table
					if(reversalstatus != "error")
						sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='reversed' WHERE transaction_id='%s'" % (transactionid)
						mysqlcursor.execute(sql)
						mysqlcon.commit()
						print "<br><br>Transaction reversed: $transactionid";
					else
						##the user doesn't have enough to reverse the transaction, they must have spent it in another way.
						sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s'" % (transactionid)
						mysqlcursor.execute(sql)
						mysqlcon.commit()
						print "<br><br>Transaction completed (user already spent funds): $transactionid"
				else
					## the receiver doesn't have enough.  They must have already spent it
					##mark as completed instead of reversed.
					sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s'" % (transactionid)
					mysqlcursor.execute(sql)
					mysqlcon.commit()
					print "<br><br>Transaction completed (user already spent funds): $transactionid";
			

		
		
		#Get ready to send out weekly notifications to users who have pending transactions to them that they need to accept.
		##get TRANSACTIONS_NOTIFIED timestamp from TEST_TABLE_RECENT
		sql = "SELECT * FROM TEST_TABLE_RECENT WHERE type='TRANSACTIONS_NOTIFIED'"
		mysqlcursor.execute(sql)
		results = mysqlcursor.fetchall()
		for row in results:
			lasttransactionsnotifiedtimestamp = row[?]
			print "<br>Last Notify Time: $lasttransactionsnotifiedtimestamp"
		
		
	
		
		##do notifications weekly, not daily.
		if ((lasttransactionsnotifiedtimestamp+(notifytransactionsinterval)) <= time.time())
			print "<br><br>Going through each user to see if need to notify"
	
			##go through each user and compile list of pending transactions to them.
			sql = "SELECT * FROM TEST_TABLE_USERS WHERE 1"
			mysqlcursor.execute(sql)
			result = mysqlcursor.fetchall()
			for row in result:
				username = row[?]
				havependingtransaction = 0
				
				$sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE receiver_username='%s' AND status='pending' ORDER BY timestamp ASC" % (username)
				mysqlcursor.execute(sql)
				resultb = mysqlcursor.fetchall()
				for row in resultb:
					havependingtransaction = 1
					oldesttransaction = row[?]
			
				if ($havependingtransaction==1)
				
					print "<br><br>$username has a pending transaction"
					message = "One or more of your received tips is pending.  If you do not take action, your account will be charged and the tip will be returned to the sender.  To finalize your ownership of the tip, send a message to bitcointip with ACCEPT in the message body.  The oldest pending tip(s) will be returned to the sender in ~%d days." % (round((oldesttransaction+(canceltransactionsinterval) - time.time())/(60*60*24)))
					
					##Add on a list of transactions since $oldesttransaction
					##add first line of transaction table headers to the response.
					transactionhistorymessage = "\n#**%s's Pending Transaction History***\n\nDate | Sender | Receiver | BTC | ~USD | Status |\n|:|:|:|:|:|:|\n" % (username)
					k = 0

					sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE (sender_username='%s' OR receiver_username='%s' ) AND timestamp>=%d ORDER BY timestamp DESC" % (username, username, oldesttransaction)
					mysqlcursor.execute(sql)
					resultc = mysqlcursor.fetchall()
					for row in resultc:
						if (k<10):
							sender = $rowtransactions['sender_username'];
							receiver_username = row[?]
							receiver_address = row[?]
							amount_BTC = row[?]
							amount_USD = row[?]
							status = row[?]
							timestamp = row[?]
							
							##if tip is sent directly to address with no username, display address.
							if (receiver_username == ""):
								receiver = receiver_address
							else:
								receiver = receiver_username
								
							date = time.date("D M d, Y", $timestamp)#todo python equivalent

							##add new transaction row to table being given to user
							newrow = "| %s | %s | %s | %d | $%d | %s |\n" % (date, sender, receiver, amount_BTC, amount_USD, status)
							transactionhistorymessage = transactionhistorymessage + newrow
						else:
							#k = 10
							transactionhistorymessage = transactionhistorymessage + "**Transaction History Truncated.*\n\n"
						k+=1
					
						
		
					transactionhistorymessage = transactionhistorymessage + "**Only includes tips to or from your Reddit username.*\n\n"
		
					message = message + transactionhistorymessage
				
					##ALL MESSAGES ADD FOOTER TO END OF ANY MESSAGE
				
					usernameaddress = bitcoind.getuseraddress(username)
					usernamebalance = bitcoind.getuserbalance(username)
					usernameusdbalance = usernamebalance*exchangerate
				
					$message = message + "\n\n---\n\n|||\n|:|:|\n| Username: | **%s** |\n| Deposit Address: | **%s** |\n| Address Balance: | **%s BTC** *(~%s USD)* |\n\n[About Bitcointip](http://www.reddit.com/r/test/comments/11ei62/bitcointip_tip_redditors_with_bitcoin/)" % (username, usernameaddress, usernamebalance, usernameusdbalance)
				
					##put message in to submit table
					sql = "INSERT INTO TEST_TABLE_TOSUBMIT (type, replyto, subject, text, captchaid, captchasol, sent, timestamp) VALUES ('message', '%s', 'Bitcointip Pending Transaction(s) Notice', '%s', '', '', '0', '%d')" % (username, message, time.time())
					mysqlcursor.execute(sql)
					mysqlcon.commit()
				
					print "<br><br>Notification of Pending transactions prepared for $username";
					
				
		
			if (lasttransactionsnotifiedtimestamp == 0):
				##if listing doesn't exist, insert
				sql = "INSERT INTO TEST_TABLE_RECENT (type,timestamp) values('TRANSACTIONS_NOTIFIED', '%d')" % (time.time())
				mysqlcursor.execute(sql)
				mysqlcon.commit()
				print "<br><br>TRANSACTIONS_INSERTED(NOTIFIED) to "
				
			else:
				
				##else update
				sql = "UPDATE TEST_TABLE_RECENT SET timestamp='%d' WHERE type='TRANSACTIONS_NOTIFIED'" % (time.time())
				mysqlcursor.execute(sql)
				mysqlcon.commit()
				print "<br><br>TRANSACTIONS_UPDATED(NOTIFIED) to "
				
			
		else:
		
			print "Not time to send notifications yet.";
			
	
	
	
	
	
		##update TRANSACTIONS_UPDATED timestamp from TEST_TABLE_RECENT to time()
		if (lasttransactionsupdatedtimestamp == 0):
			##if listing doesn't exist, insert
			sql = "INSERT INTO TEST_TABLE_RECENT (type,timestamp) values('TRANSACTIONS_UPDATED', '"%d"')" % (time.time())
			mysqlcursor.execute(sql)
			mysqlcon.commit()
			print "<br><br>TRANSACTIONS_INSERTED(UPDATED) to "
			
		else:
			##else update
			sql = "UPDATE TEST_TABLE_RECENT SET timestamp='%d' WHERE type='TRANSACTIONS_UPDATED'" % (time.time())
			mysqlcursor.execute(sql)
			mysqlcon.commit()
			print "<br><br>TRANSACTIONS_UPDATED(UPDATED) to "
	else:
		print "<br><br> Hasn't beena day yet.";
	

#find_message_command
#returns text result as message to send back.
def find_message_command(themessage): #array
	
	body = themessage[body]
	author = themessage[author]
	
	if (botstatus == "down")
		returnstring "The bitcointip bot is currently down.\n\n[Click here for more information about the bot.](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/)\n\n[Click here for more information about bitcoin.](http:##www.weusecoins.com/)\n\n[Click here to get a bitcoin wallet.](https:##blockchain.info/wallet/)"
		return returnstring
	
	#See if the message author has a bitcointip account, if not, make one for them.
	sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='$author'"
	mysqlcursor.execute(sql)
	result = mysqlcursor.fetchall()
	for row in result:
		userhasaccount = 1

	if (userhasaccount == 0)
		adduser(author)
	
	
	#Start going through the message for commands. Only the first found will be evaluated
	
	#"REDEEM KARMA: 1thisisabitcoinaddresshereyes"
	#"TRANSACTIONS"/"HISTORY"/"ACTIVITY"
	#"EXPORT ACCOUNT"
	#"IMPORT ACCOUNT"
	#ANY COMMAND OR NO COMMAND
	

	
	#"REDEEM KARMA: 1thisisabitcoinaddresshereyes"
	#if bitcoinaddress is valid, 
	regex = re.compile("REDEEM( )?KARMA:( )?(1([A-Za-z0-9]{25,35}))",re.IGNORECASE)
	command = regex.search(body)
	
	if (!command and returnstring==""):
		
		#karma redemption command found
		karmabitcoinaddress = command[2]
		
		
		#karma limits on which redditors can get bitcoins for their karma
		minlinkkarma = 0
		mincommentkarma = 200
		mintotalkarma = 200

		#baseline amount of bitcoin to give each redditor (enough to cover some mining fees)
		defaultbitcoinamount = 0.00200000


		#get balance of bitcoinfaucet
		faucetbalance = getuserbalance("bitcointipfaucetdepositaddress")
		
		
		
		if ( userhasredeemedkarma(author) == 0 ):
			#if not redeemed yet, check for a valid bitcoin address

			print "user has not redeemed karma yet."

			if ( bitcoind.validateaddress(karmabitcoinaddress) == 1 ):
			
				#valid bitcoin address detected

				#get user's link karma and comment karms
				print "Valid bitcoin address detected: $karmabitcoinaddress."
				
				
				#praw
				user = reddit.get_redditor(author)
				
				
				linkkarma = user.link_karma
				commentkarma = user.comment_karma
				totalkarma = linkkarma + commentkarma
	
				

				#format all the bitcoin amounts correctly for messages and displaying and storage
				
				#calculate how many bitcoins they might get from karma
				karmabitcoinamount = round((totalkarma/(100000000)),8)
				#print "bitcoin amount: ".number_format($karmabitcoinamount, 8, ".", "");
				
				#only give valid reddit users any bitcoins (check that karma is above a certain amount)
				if ( linkkarma>minlinkkarma and commentkarma>mincommentkarma and totalkarma>mintotalkarma):
					#User has enough karma
					print "user has enough karma"
					
					if ( karmabitcoinamount < 0.002 )
						 bitcoinamount = karmabitcoinamount +defaultbitcoinamount
						print "give user defualt amount too."
					else:
						bitcoinamount = karmabitcoinamount;
						print "don't give user default amount.";
					
					#check to make sure the faucet has enough.
					if ( faucetbalance > (bitcoinamount+0.0005) ):
						
						#The reddit bitcoin faucet has enough
						print "the reddit bitcoin faucet has: $faucetbalance."

						#go ahead and send the bitcoins to the user
						status = bitcoind.transact("bitcointipfaucetdepositaddress", karmabitcoinaddress, bitcoinamount)

						if (status != "error"):
							print "no error, transaction done, bitcoins en route.";
							#reply to their message with success
							returnstring = "Your bitcoins are on their way.  Check the status here: http://blockchain.info/address/$karmabitcoinaddress\n\nIf you do not want your bitcoins, consider donating them to a [good cause](https://en.bitcoin.it/wiki/Donation-accepting_organizations_and_projects)."
							
							#insert the transaction to the list of TABLE_FAUCET_PAYOUTS
							sql = "INSERT INTO TEST_TABLE_FAUCET_PAYOUTS (transaction_id, username, address, amount, timestamp) VALUES ('%s', '%s', '%s', '%d', '%d')" % (status, author, karmabitcoinaddress, bitcoinamount, time.time())
							mysqlcursor.execute(sql)
							mysqlcon.commit()

						else:
							#there was an error with blockchain, have the user try again later maybe.
							print "error with the blockchain."
							#say so.
							returnstring = "The Reddit Bitcoin Faucet is down temporarily.  Try again another day."

					else:
						#faucet is out of bitcoins.
						#say so.
						returnstring = "The Reddit Bitcoin Faucet is out of bitcoins until someone donates more. View the balance [here](http://blockchain.info/address/13x9weHkPTFL2TogQJz7LbpEsvpQJ1dxfa)."
					
				else:

					#user doesn't have enough karma
					print "User doesn't have enough karma."
					returnstring = "You do not have enough karma to get bitcoins. You need at least $mincommentkarma Comment Karma to be eligible (You only have $commentkarma). Keep redditing or try this bitcoin faucet: https://freebitcoins.appspot.com"

			else:
				#no valid bitcoin address detected
				print "No valid bitcon address detected."
				returnstring = "No valid bitcoin address detected.  Send the string \"REDEEM KARMA: 1YourBitcoinAddressHere\" please."

		else:
			print "User has already redeemed karma"
			#user has already redeemed karma, can't do it again.
			returnstring = "You have already sold your karma for bitcoins.  You can only do this once."
	
	
	#"TRANSACTIONS"/"HISTORY"/"ACTIVITY"
	#Gives use a list of their transactions including deposits/withdrawals/sent/recieved
	regex = re.compile("((TRANSACTIONS)|(HISTORY)|(ACTIVITY))",re.IGNORECASE)
	command = regex.search(body)
	
	if (!command and returnstring==""):
		
		#add first line of transaction table headers to the response.
		transactionhistorymessage = "\n#**%s Transaction History***\n\nDate | Sender | Receiver | BTC | ~USD | Status |\n|:|:|:|:|:|:|\n" % (author)
		k = 0

		sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE sender_username='%s' OR receiver_username='%s' ORDER BY timestamp DESC" % (author, author)
		mysqlcursor.execute(sql)
		result = mysqlcursor.fetchall()
		for row in result:
			if (k<11):
				sender = row[?]
				receiver_username = row[?]
				receiver_address = row[?]
				amount_BTC = row[?]
				amount_USD = row[?]
				status = row[?]
				timestamp = row[?]
				
				##if tip is sent directly to address with no username, display address.
				if (receiver_username == ""):
					receiver = receiver_address
				else:
					receiver = receiver_username
				
				date = date("D M d, Y", $timestamp);#todo python
				
				
				if (sender == author):
					senderbold = "**"
					amountsign = "*"
				else if (receiver == author):
					receiverbold = "**"
					amountsign = "**"
					
				##add new transaction row to table being given to user
				newrow = "| %s | %s%s%s | %s%s%s | %s%s%s | %s$%s%s | %s |\n" % (date, senderbold, sender, senderbold, receiverbold, receiver, receiverbold, amountsign, amount_BTC, amountsign, amountsign, amount_USD, amountsign, status)
				transactionhistorymessage = transactionhistorymessage + newrow;

			else if (k == 11):
				##if there are more than 30 transactions, tell them there are some left out after the table.
				transactionhistorymessage = transactionhistorymessage + "**Transaction History Truncated.*\n\n"
				break
			k++

			##end
		
		#if no transactions, say so
		if (k == 0)
			transactionhistorymessage += "\n\n**You have no transactions.**\n\n"

		
		transactionhistorymessage += "\n**Only includes tips to or from your Reddit username.*\n\n\n"
		
		returnstring += transactionhistorymessage

	#REPLACE TODO
	###"REPLACE PRIVATE KEY WITH: $privatekey
	###TRANSFER BALANCE: Y/N"
	
	regex = re.compile("((REPLACE PRIVATE KEY WITH:)( )?(5[a-zA-Z0-9]{35,60})(( )*(\n)*( )*)(TRANSFER BALANCE:)( )?(Y|N))",re.IGNORECASE)
	command = regex.search(body)
	
	if (!command and returnstring==""):

		if (getusergiftamount(author) >= 0.5):
		#do it
		
			print "<br>Private Key detected...";
			privatekey = command.groups[3]
			transfer = command.groups[10]
			
			print "<br>Private Key:$privatekey..."
			print "<br>Transfer: $transfer..."
			
			authoroldaddress = getuseraddress(author)
			authoroldbalance = getuserbalance(author)
			
			print "<br>authoroldaddress: $authoroldaddress..."
			print "<br>authoroldbalance: $authoroldbalance..."
			
			
			
			
			importsuccessful = (bitcoind.importprivkey($privatekey, "thisisatemporarylabelthatnobodyshoulduse"))
			
			print "<br>importsuccessful: $importsuccessful"
			
				if (importsuccessful == true):
			
				authornewaddress = bitcoind.getaccountaddresstemp("thisisatemporarylabelthatnobodyshoulduse")
				authornewbalance = bitcoind.getbalance("thisisatemporarylabelthatnobodyshoulduse")
				
				print "<br>authornewaddress: $authornewaddress..."
				print "<br>authornewbalance: $authornewbalance..."
			
				setaccountold = bitcoind.setaccount(authoroldaddress, "OLD ADDRESS: "+author);
				setaccountnew = bitcoind.setaccount(authornewaddress, author);
				
				print "<br>setaccountold: $setaccountold..."
				print "<br>setaccountnew: $setaccountnew..."
				
				
				if (setaccountold == true and setaccountnew == true):
				
					returnstring = "Replacement successful. Your new bitcoin address is: %s.\n\nYour old bitcoin address was: ~~%s~~." % (authornewaddress, authoroldaddress)
				if (transfer.lower == "y" and authoroldbalance != 0):
					moveamount = authoroldbalance - 0.0005
					moved = bitcoind.move(authoroldaddress, authornewaddress, moveamount) 
					print "<br>moved: $moved..."
					if (moved != "error"):
						returnstring += "\n\nYour old balance of %s is being moved to your new address." % (moveamount)
						authornewbalance += moveamount
					else	
						returnstring += "\n\nThere was a problem moving your funds. Either you have too little or something went wrong."
			
				##update user table entry with new balance and new address

				sql = "UPDATE TEST_TABLE_USERS SET address='$authornewaddress' WHERE username='$author'" % (authornewaddress, author)
				mysqlcursor.execute(sql)
				mysqlcon.commit()
				
			else:
				returnstring = "There was a problem setting up your new account."
		
		else:
			returnstring = "There was a problem importing the private key.  Make sure it is in Sipa wallet format and begins with a '5'."

		else:
		##not enough gift.
		returnstring = "You have not donated enough to use that command." 	
	
	##ACCEPT PENDING TRANSACTIONS
	##"ACCEPT"
	regex = re.compile("(ACCEPT)",re.IGNORECASE)
	command = regex.search(body)
	
	if (!command and returnstring==""):
		update_lastactive($author);
		returnstring = "All pending transactions will be accepted.  No currently existing tips to you will be reversed."
	

	
##CHECK FOR MESSAGE TIP (take care of sending all messages here, return empty string, telling eval_messages to not send any more messages.
	
##regex expression for a tip "+bitcointip username amount verify"

##TODO this regex isn't working in python, but does in PHP, what's wrong?

	regex = re.compile("(\+((bitcointip)|(bitcoin)|(tip)|(btctip)|(bittip)|(btc))( ((1([A-Za-z0-9]{25,35}))||((@)?[A-Za-z0-9_-]{4,20})))( ((((((\$)?(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD))|(((\$)(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD)?))|(((((B)|(&amp;#3647;))(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC)?)|(((B)|(&amp;#3647;))?(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC)))))|(ALL\b)))( NOVERIFY)?)",re.IGNORECASE)
	command = regex.search(body)
	
	if (!command and returnstring==""):
		##message contains transaction
		print "<br>message contains tip!"
		
		
		##get initial info
		tipsenderusername = themessage[author]
		tiptimestamp = themessage[created_utc]
		tipurl = themessage[name]
		tipsubreddit = ""
		tipsenderaddress = getuseraddress(tipsenderusername)
		tipbitcoinamount = ""
		tipdollaramount = ""
		tipreceiverusername = ""
		tipreceiveraddress = ""
		##this is a message
		tiptype = "message"
		tipstatus = ""
		tipstatusmessage = ""
		
		#if a pm contains a tip, always send verify messages
		if (tiptype == "message"):
			tipverify = "verify"
		
		##isolate the tipping command
		tipstring = command.groups[?]
		
		print "<br>Tipstring: '$tipstring'";

		receiverusernameregex = re.compile("( (@)?([A-Za-z0-9_-]{4,20}) )",re.IGNORECASE)
		
		receiveraddressregex = re.compile("( (1([A-Za-z0-9]{25,35})) )",re.IGNORECASE)
		
		dollaramountregex = re.compile("( ((((\$)?(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD))|(((\$)(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD)?)))",re.IGNORECASE)
		
		bitcoinamountregex = re.compile("( ((((B)|(&amp;#3647;))(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC)?)|(((B)|(&amp;#3647;))?(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC))))",re.IGNORECASE)
		
		verifyregex = re.compile("( (NOVERIFY))",re.IGNORECASE)
		
		allregex = re.compile("( (ALL\b))",re.IGNORECASE)
		
		flipregex = re.compile("( (FLIP\b))",re.IGNORECASE)
		
		##are these things included?
		includereceiverusername = 0
		includereceiveraddress = 0
		includedollaramount = 0
		includebitcoinamount = 0
		includeverify = 1
		



		receiverusernamearray = receiverusernameregex.search(tipstring)
		receiveraddressarray = receiveraddressregex.search(tipstring)
		dollaramountarray = dollaramountregex.search(tipstring)
		bitcoinamountarray = bitcoinamountregex.search(tipstring)
		verifyarray = verifyregex.search(tipstring)
		allarray = allregex.search(tipstring)
		fliparray = flipregex.search(tipstring)
		
		
		##does $tipstring contain receiverusername?
		if (!receiverusernamearray):
			includereceiverusername = 1
			tipreceiverusername = receiverusernamearray.groups[0]
			tipreceiverusername = trim($tipreceiverusername," @")
			print "<br>receiverusername:$tipreceiverusername"

		##does $tipstring contain receiveraddress?
		if (preg_match($receiveraddressregex, $tipstring, $receiveraddressarray)==1)
		{
			$includereceiveraddress=1;
			$tipreceiveraddress=$receiveraddressarray[2];
			print "<br>receiveraddress:$tipreceiveraddress";
		}

		##does $tipstring contain dollaramount?
		if (preg_match($dollaramountregex, $tipstring, $dollaramountarray)==1)
		{
			$includedollaramount=1;
			$tipdollaramount=$dollaramountarray[1];
			
			##strip dollar amount of extraneous characters
			$tipdollaramount= trim($tipdollaramount, "$ USDusd,");
			print "<br>dollar amount:$tipdollaramount";
		}

		##does $tipstring contain bitcoinamount?
		if (preg_match($bitcoinamountregex, $tipstring, $bitcoinamountarray)==1)
		{
			$includebitcoinamount=1;
			$tipbitcoinamount=$bitcoinamountarray[1];
			
			##strip of the special symbol
			$tipbitcoinamount = str_replace("&amp;#3647;", "", $tipbitcoinamount);
			
			##strip bitcoin amount of extraneous characters
			$tipbitcoinamount= trim($tipbitcoinamount, "B BTCbtc,");
			print "<br>bitcoinamount:$tipbitcoinamount";
		}


		
		##does $tipstring contain amount keyword "all"?
		if (preg_match($allregex, $tipstring, $allarray)==1)
		{
		

				$senderbalance=getuserbalance($tipsenderusername);
				$amount=($senderbalance - 0.0005);
				$amount=round($amount, 8);
				$tipbitcoinamount=$amount;
				$includebitcoinamount=1;
			
			
		}
		
		


			
			
		
		
		
		
		
		##does $tipstring contain verify?
		if (preg_match($verifyregex, $tipstring, $verifyarray)==1)
		{
			$includeverify=0;
			$tipverify=$verifyarray[2];
			print "<br>verify:$tipverify";
		}

		print "<br>Now getting the information gaps.";
		##based on what the tip command contains, fill in the information gaps.

		if ($includereceiveraddress==0 && $includereceiverusername==0 && $tiptype=="comment")
		{
		

		}

		if ($includebitcoinamount==1)
		{
		
			$tipdollaramount=$tipbitcoinamount*$exchangerate;
			##round to 2 decimals
			$tipdollaramount=round($tipdollaramount,2);
			print "<br>dollaramount:$tipdollaramount";
		}
		else
		{
			$tipbitcoinamount=$tipdollaramount/$exchangerate;
			##round to 8 decimals
			$tipbitcoinamount=round($tipbitcoinamount,8);
			print "<br>bitcoinamount:$tipbitcoinamount";
		}

		if ($includereceiverusername==1)
		{
			##get $receiveraddress from table if user is in table_users
			$tipreceiveraddress=getuseraddress($tipreceiverusername);
			print "<br>receiveraddress:$tipreceiveraddress";
		}




		##check conditions to cancel the transaction and return error message

		##transaction amount is 0 BTC
		if ($tipbitcoinamount==0)
		{
			$cancelmessage="You cannot send an amount of 0. That is just silly.";
			##cancel transaction
			$validtransaction="no";

		}

		##Sender doesn't have (BTC amount +0.0005) in their account
		##get sender balance
		$totalneeded=$tipbitcoinamount+0.0005;
		$senderbalance=getuserbalance($tipsenderusername);
		if ($totalneeded>$senderbalance)
		{
			$cancelmessage="You do not have enough in your account.  You have $senderbalance BTC, but need $totalneeded BTC (do not forget about the 0.0005 BTC fee per transaction).";
			##cancel transaction
			$validtransaction="no";
		}

		##Not in supported subreddit
		if ( $tiptype=="comment" && (checksubreddit($tipsubreddit)==0) && (getusergiftamount($tipsenderusername)<2) )
		{
			$cancelmessage="The $tipsubreddit subreddit is not currently supported.";
			##cancel transaction
			$validtransaction="no";
		}
		
		##Sender is Banned
		if (checkuser($tipsenderusername)==0 && $tipsenderusername!="")
		{
			$cancelmessage="You are not allowed to send or receive money.";
			##cancel transaction
			$validtransaction="no";
		}

		##Receiver is Banned
		if (checkuser($tipreceiverusername)==0 && $tipreceiverusername!=""){

			if (checkuser($tipreceiverusername)==0){
				$cancelmessage="The user $tipreceiverusername is not allowed to send or receive money.";
				##cancel transaction
				$validtransaction="no";
			}

		}
		
		if ($tipreceiverusername==$tipsenderusername){
		$cancelmessage="You cannot send any amount to yourself, that is just silly.";
		##canceltransaction
		$validtransaction="no";
		}
		
		if ($tipreceiverusername=="" && $tipreceiveraddress==""){
			$cancelmessage="You must specify a recipient username or bitcoin address";
			##canceltransaction
			$validtransaction="no";
		}


print "<br>validtransaction:$validtransaction";
		print "<br>cancel message:$cancelmessage";
		
		
		
		##do transaction if valid
		##then send any messages that need sending.
				if ($validtransaction!="no"){


			##tipreceiverusername
			##tipreceiveraddress
			##tipsenderusername
			##tipsenderaddress
			##tipbitcoinamount
			##tipdollaramount
			##tiptype
			##tipurl
			##tiptimestamp
			##tipsubreddit
			##tipverify
			##tipstatus
			##tipstatusmessage
			
			##returns "cancelled" or "pending"
$transactionstatus=dotransaction($tipsenderusername,$tipsenderaddress,$tipreceiverusername,$tipreceiveraddress,$tipbitcoinamount,$tipdollaramount,$tiptype,$tipurl,$tiptimestamp,$tipsubreddit,$tipverify,$tipstatus,$tipstatusmessage);
			
			if ($transactionstatus=="cancelled")
			$cancelmessage="There was an error that probably was not your fault.";
			
			##based on status, create end result fail/success
			if ($transactionstatus=="cancelled")
			$transactionresult="fail";
			else
			$transactionresult="success";
			
			}
			else
			{
			$transactionresult="fail";
			}
			
			
##by the time we get here, the following variables must be defined:

##tiptype yes
##includeverify yes
##transactionresult
##commentid if type=comment

print "<br>transactionresult:$transactionresult";
print "<br>tipreceiverusername:$tipreceiverusername";
print "<br>tipreceiveraddress:$tipreceiveraddress";
print "<br>includeverify:$includeverify";
print "<br>tiptype:$tiptype";

if ($transactionresult!=""){


	if ($tipreceiverusername=="")
		$tipreceiver=$tipreceiveraddress;
	else
		$tipreceiver=$tipreceiverusername;
		

    
    if ($transactionresult=="success"){
        
                        $rejectverify="Verified";
            $strikethrough="";
    }else if ($transactionresult=="fail")
    {
                        $rejectverify="Failed";
            $strikethrough="~~";
    }
    
	 $message="Transaction $rejectverify!\n\n$strikethrough**$tipsenderusername --> $tipbitcoinamount BTC *(~$$tipdollaramount USD)* --> $tipreceiver**$strikethrough";
	 
	 	
		if ($transactionresult=="success")
		$subject="Successful Bitcointip Notice";

		if ($transactionresult=="fail")
		$subject="Failed Bitcointip Notice";
		
	 
	 
	if ( ($transactionresult=="fail") || ($includeverify==1) ){
	##PM Sender
	
	##only send cancelreason to sender
	$sendermessage=$message."\n\n".$cancelmessage;
	
	
		$senderaddress=getuseraddress($tipsenderusername);
		$senderbalance=getuserbalance($tipsenderusername);
		$senderUSDbalance=$senderbalance*getExchangeRate("mtgoxUSD");
		$senderbalance=number_format($senderbalance, 8, ".", "");
		$senderUSDbalance=number_format($senderUSDbalance, 2, ".", "");
	
	$sendermessage.="\n\n---\n\n|||
|:|:|
| Account Owner: | **$tipsenderusername** |
| Deposit Address: | **$senderaddress** |
| Address Balance: | **$senderbalance BTC** *(~$$senderUSDbalance USD)* |"."\n\n[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/) (BETA!)";
	
	
		
				print "<br>submitting a message";

		mysql_query("INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp) 
	VALUES ('', 'message', '$tipsenderusername', '$subject', '$sendermessage', '', '', '0', '".time()."')",$con);

	}
	
	if ($transactionresult=="success" && $tipreceiverusername!="")
	{
	##if the transaction went through, send a message to the receiver if there is one.
	
$receiveraddress=getuseraddress($tipreceiverusername);
		$receiverbalance=getuserbalance($tipreceiverusername);
		$receiverUSDbalance=$receiverbalance*getExchangeRate("mtgoxUSD");
		$receiverbalance=number_format($receiverbalance, 8, ".", "");
		$receiverUSDbalance=number_format($receiverUSDbalance, 2, ".", "");
	
	$receivermessage=$message."\n\n---\n\n|||
|:|:|
| Account Owner: | **$tipreceiverusername** |
| Deposit Address: | **$receiveraddress** |
| Address Balance: | **$receiverbalance BTC** *(~$$receiverUSDbalance USD)* |"."\n\n[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/) (BETA!)";
		 
		 		mysql_query("INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp) 
	VALUES ('', 'message', '$tipreceiverusername', '$subject', '$receivermessage', '', '', '0', '".time()."')",$con);
	
	}


}

			
	return "";
	}
	else
	{
		##/this comment contains no "+bitcointip" or a "+1 internet"

	}
	
	
	
		##HELP
		if(preg_match('/HELP/i', $body, $command) && returnstring=="")
	{
	returnstring="Check the [Help Page](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/).";
	}
	
	
		##NO COMMAND DO YOU NEED HELP?
	##"blah blah blah"
	if (returnstring==""){
		
		returnstring="This is the bitcointip bot.  No command was found in your message.\n\nTo fund your account, send bitcoins to your Deposit Address.\n\nFor help with commands, see [This Page](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/).\n\n*Replies from the bot take on average 7.5 minutes but may take 30 minutes or more in some cases.*\n\n*Deposits are updated once per hour.*";
		
	}
	
	

	##ALL MESSAGES ADD FOOTER TO END OF ANY MESSAGE
	
$authorbalance=getuserbalance($author);
$authoraddress=getuseraddress($author);
	
	$authorbalance=number_format($authorbalance, 8, ".", "");
	$authorUSDbalance=number_format($authorUSDbalance, 2, ".", "");
	
	returnstring.="\n\n---\n\n|||
|:|:|
| Account Owner: | **$author** |
| Deposit Address: | **$authoraddress** |
| Address Balance: | **$authorbalance BTC** *(~$$authorUSDbalance USD)* |"."\n\n
[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/) (BETA!)";

	
	return returnstring;
	
}





#eval_messages
# get new messages and go through each one looking for a command, then respond.
def eval_messages():
	#TODO
	#get all the messages that haven't yet been gotten.
	
	#go through all those messages oldest to newest and do find_message_command(messagedataarray) on each comment
	find_message_command(messagedataarray)
	
	#then when done, log the timestamp of the last message evaluated.
	# we'll start with that message next time around.




#find_comment_command
#find a command in a user comment
function find_comment_command($comment)
{

	##bring the current mtgox exchange rate into the function
	global $exchangerate;

	##connection variables
	global $reddit, $con, $botid;


	##comment tip YES
		##regex expression for a tip "+bitcointip username amount verify"
	$tipregex='/(\+((bitcointip)|(bitcoin)|(tip)|(btctip)|(bittip)|(btc))( ((1([A-Za-z0-9]{25,35}))||((@)?[A-Za-z0-9_-]{4,20})))?( ((((((\$)?(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD))|(((\$)(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD)?))|(((((B)|(&amp;#3647;))(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC)?)|(((B)|(&amp;#3647;))?(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC)))))|(ALL\b)|(FLIP\b)))( NOVERIFY)?)|(\+1 internet(s)?)/i';

	if(preg_match($tipregex, $comment[body], $tiparray)==true)
	{
		##message contains transaction
		print "<br>message contains tip!";
		
		
		##get initial info
		$tipsenderusername=$comment[author];
		$tiptimestamp=$comment[created_utc];
		$tipurl=$comment[name];
		$tipsubreddit=$comment[subreddit];
		$tipsenderaddress=getuseraddress($tipsenderusername);
		$tipbitcoinamount="";
		$tipdollaramount="";
		$tipreceiverusername="";
		$tipreceiveraddress="";
		##this is a comment
		$tiptype="comment";
		$tipstatus="";
		$tipstatusmessage="";

		$tipverify="verify";
		
		##get transaction info
		$tipstring=$tiparray[0];
		
		print "<br>Tipstring: '$tipstring'";

		$receiverusernameregex='/( (@)?([A-Za-z0-9_-]{4,20}) )/i';
		$receiveraddressregex='/( (1([A-Za-z0-9]{25,35})) )/i';
		$dollaramountregex='/( ((((\$)?(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD))|(((\$)(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD)?)))/i';
		$bitcoinamountregex='/( ((((B)|(&amp;#3647;))(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC)?)|(((B)|(&amp;#3647;))?(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC))))/i';
		$verifyregex='/( (NOVERIFY))/i';
		$allregex='/( (ALL\b))/i';
		$internetregex='/(\+1 internet(s)?)/i';
		$flipregex='/( (FLIP\b))/i';

		##are these things included?
		$includereceiverusername=0;
		$includereceiveraddress=0;
		$includedollaramount=0;
		$includebitcoinamount=0;
		$includeverify=1;
		$includeinternet=0;
		$includeflip=0;
		




		##does $tipstring contain receiverusername?
		if (preg_match($receiverusernameregex, $tipstring, $receiverusernamearray)==1)
		{
			$includereceiverusername=1;
			$tipreceiverusername=$receiverusernamearray[0];
			$tipreceiverusername=trim($tipreceiverusername," @");
			print "<br>receiverusername:$tipreceiverusername";
		}

		##does $tipstring contain receiveraddress?
		if (preg_match($receiveraddressregex, $tipstring, $receiveraddressarray)==1)
		{
			$includereceiveraddress=1;
			$tipreceiveraddress=$receiveraddressarray[2];
			print "<br>receiveraddress:$tipreceiveraddress";
		}

		##does $tipstring contain dollaramount?
		if (preg_match($dollaramountregex, $tipstring, $dollaramountarray)==1)
		{
			$includedollaramount=1;
			$tipdollaramount=$dollaramountarray[1];
			
			##strip dollar amount of extraneous characters
			$tipdollaramount= trim($tipdollaramount, "$ USDusd,");
			print "<br>dollar amount:$tipdollaramount";
		}

		##does $tipstring contain bitcoinamount?
		if (preg_match($bitcoinamountregex, $tipstring, $bitcoinamountarray)==1)
		{
			$includebitcoinamount=1;
			$tipbitcoinamount=$bitcoinamountarray[1];
			
			##strip of the special symbol
			$tipbitcoinamount = str_replace("&amp;#3647;", "", $tipbitcoinamount);
			
			##strip bitcoin amount of extraneous characters
			$tipbitcoinamount= trim($tipbitcoinamount, "B BTCbtc,");
			print "<br>bitcoinamount:$tipbitcoinamount";
		}


		##does $tipstring contain amount keyword "all"?
		if (preg_match($allregex, $tipstring, $allarray)==1)
		{
		
				print "<br>ALL FOUND";
				$senderbalance=getuserbalance($tipsenderusername);
				$amount=($senderbalance - 0.0005);
				$amount=round($amount, 8);
				$tipbitcoinamount=$amount;
				$includebitcoinamount=1;
		}
		
		
			##does $tipstring contain amount keyword "flip"?
		if (preg_match($flipregex, $tipstring, $fliparray)==1)
		{
		$includeflip=1;
		if (getusergiftamount($tipsenderusername)>=0.25){
		
				$senderbalance=getuserbalance($tipsenderusername);
				
				if ($senderbalance>=(0.01+0.0005))
				{
				##do a coin flip
				$flip=round(rand(0,1));
				
				if ($flip==1)
				{
				##flip is 1
				##tip the person
				$tipbitcoinamount=0.01;
				$includebitcoinamount=1;
				}
				else
				{
				##flip is 0
				##no tip
				$tipbitcoinamount=0;
				$includebitcoinamount=1;
				}
				}
				else
				{
				##not enough
				##do a 0 tip.
				$flip=-1;
				$tipbitcoinamount=0;
				$includebitcoinamount=1;
				}
				}
				else
				{
				##not authorized
				return "";
				}
				
				
		}
		
		
		##does $tipstring contain "+1 internet(s)"?
				if (preg_match($internetregex, $tipstring, $internetarray)==1)
		{
		
		if (getusergiftamount($tipsenderusername)>=1){
print "<br>+1 internet(s) detected.";
		$internetqty=$internetarray[0];
		
		if (preg_match("/\+1 internet/i", $internetqty, $internetqtyarray)==1)
		$tipbitcoinamount=0.01;
		if (preg_match("/\+1 internets/i", $internetqty, $internetqtyarray)==1)
		$tipbitcoinamount=0.02;
		
		$includebitcoinamount=1;
		$includeinternet=1;
		}
		else
		{
		##ignore this comment todo
		return "";
		}
	
		}
		
		
		
		##does $tipstring contain verify?
		if (preg_match($verifyregex, $tipstring, $verifyarray)==1)
		{
			$includeverify=0;
			$tipverify=$verifyarray[2];
			print "<br>verify:$tipverify";
		}

		print "<br>Now getting the information gaps.";
		##based on what the tip command contains, fill in the information gaps.

		if ($includereceiveraddress==0 && $includereceiverusername==0 && $tiptype=="comment")
		{
		
		print "<br>Getting author of parentid";
		receiverusername = ??????????????????#praw?
		
		}

		if ($includebitcoinamount==1)
		{
		
			$tipdollaramount=$tipbitcoinamount*$exchangerate;
			##round to 2 decimals
			$tipdollaramount=round($tipdollaramount,2);
			print "<br>dollaramount:$tipdollaramount";
		}
		else
		{
			$tipbitcoinamount=$tipdollaramount/$exchangerate;
			##round to 8 decimals
			$tipbitcoinamount=round($tipbitcoinamount,8);
			print "<br>bitcoinamount:$tipbitcoinamount";
		}

		if ($includereceiverusername==1)
		{
			##get $receiveraddress from table if user is in table_users
			$tipreceiveraddress=getuseraddress($tipreceiverusername);
			print "<br>receiveraddress:$tipreceiveraddress";
		}




		##check conditions to cancel the transaction and return error message

		##transaction amount is 0 BTC
		if ($tipbitcoinamount==0)
		{
			$cancelmessage="You cannot send an amount of 0. That is just silly.";
			##cancel transaction
			$validtransaction="no";

		}

		##Sender doesn't have (BTC amount +0.0005) in their account
		##get sender balance
		$totalneeded=$tipbitcoinamount+0.0005;
		$senderbalance=getuserbalance($tipsenderusername);
		if ($totalneeded>$senderbalance)
		{
			$cancelmessage="You do not have enough in your account.  You have $senderbalance BTC, but need $totalneeded BTC (do not forget about the 0.0005 BTC fee per transaction).";
			##cancel transaction
			$validtransaction="no";
		}

		##Not in supported subreddit
		if ( $tiptype=="comment" && (checksubreddit($tipsubreddit)==0) && (getusergiftamount($tipsenderusername)<2) )
		{
			$cancelmessage="The $tipsubreddit subreddit is not currently supported.";
			##cancel transaction
			$validtransaction="no";
		}
		
		##Sender is Banned
		if (checkuser($tipsenderusername)==0 && $tipsenderusername!="")
		{
			$cancelmessage="You are not allowed to send or receive money.";
			##cancel transaction
			$validtransaction="no";
		}

		##Receiver is Banned
		if (checkuser($tipreceiverusername)==0 && $tipreceiverusername!=""){

			if (checkuser($tipreceiverusername)==0){
				$cancelmessage="The user $tipreceiverusername is not allowed to send or receive money.";
				##cancel transaction
				$validtransaction="no";
			}

		}
		
		if ($tipreceiverusername==$tipsenderusername){
		$cancelmessage="You cannot send any amount to yourself, that is just silly.";
		##canceltransaction
		$validtransaction="no";
		}
		
		if ($tipreceiverusername=="" && $tipreceiveraddress==""){
			$cancelmessage="You must specify a recipient username or bitcoin address";
			##canceltransaction
			$validtransaction="no";
		}


print "<br>validtransaction:$validtransaction";
		print "<br>cancel message:$cancelmessage";
		
		
		
		##do transaction if valid
		##then send any messages that need sending.
				if ($validtransaction!="no"){


			##tipreceiverusername
			##tipreceiveraddress
			##tipsenderusername
			##tipsenderaddress
			##tipbitcoinamount
			##tipdollaramount
			##tiptype
			##tipurl
			##tiptimestamp
			##tipsubreddit
			##tipverify
			##tipstatus
			##tipstatusmessage
			
			##returns "cancelled" or "pending"
$transactionstatus=dotransaction($tipsenderusername,$tipsenderaddress,$tipreceiverusername,$tipreceiveraddress,$tipbitcoinamount,$tipdollaramount,$tiptype,$tipurl,$tiptimestamp,$tipsubreddit,$tipverify,$tipstatus,$tipstatusmessage);
			
			if ($transactionstatus=="cancelled")
			$cancelmessage="There was an error that probably was not your fault.";
			
			##based on status, create end result fail/success
			if ($transactionstatus=="cancelled")
			$transactionresult="fail";
			else
			$transactionresult="success";
			
			}
			else
			{
			$transactionresult="fail";
			}
			
			
##by the time we get here, the following variables must be defined:

##tiptype yes
##includeverify yes
##transactionresult
##commentid if type=comment

print "<br>transactionresult:$transactionresult";
print "<br>tipreceiverusername:$tipreceiverusername";
print "<br>tipreceiveraddress:$tipreceiveraddress";
print "<br>includeverify:$includeverify";
print "<br>tiptype:$tiptype";

if ($transactionresult!=""){


	if ($tipreceiverusername=="")
		$tipreceiver=$tipreceiveraddress;
	else
		$tipreceiver=$tipreceiverusername;
		

    
    if ($transactionresult=="success"){
        
                        $rejectverify="Verified";
            $strikethrough="";
    }else if ($transactionresult=="fail")
    {
                        $rejectverify="Failed";
            $strikethrough="~~";
    }
    
	##create custom replys for internets or flips
	
	if ($includeinternet==1)
	{
	
	if ($bitcoinamount==0.01)
	$internets="1 internet (0.01 BTC)";
	else if ($bitcoinamount==0.02)
	$internets="1 internets (0.02 BTC)";
	
	$reply="Transaction $rejectverify!\n\n$strikethrough**$tipsenderusername --> $internets *(~$$tipdollaramount USD)* --> $tipreceiver**$strikethrough"."\n\n[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/) ";
	}
	else if ($includeflip==1)
	{
	
	$reply="Transaction $rejectverify!\n\n$strikethrough**$tipsenderusername --> $tipbitcoinamount BTC *(~$$tipdollaramount USD)* --> $tipreceiver**$strikethrough"."\n\n[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/)";
	
	if ($flip==0)
	$reply="Bitcent landed **0** up. $tipreceiver wins nothing.\n\n"."[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/) ";
	elseif ($flip==1)
	$reply="Bitcent landed **1** up. $tipreceiver wins 1 bitcent.\n\n".$reply;
	elseif ($flip==-1)
	$reply="$tipsenderusername does not have a bitcent to flip.\n\n"."[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/) ";
	
	
	}
	else
	{
	$reply="Transaction $rejectverify!\n\n$strikethrough**$tipsenderusername --> $tipbitcoinamount BTC *(~$$tipdollaramount USD)* --> $tipreceiver**$strikethrough"."\n\n[About Bitcointip](http:##www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/) ";
	}
	
	

				
				print "Reply:$reply";


	if ($tiptype=="comment" && $includeverify==1 && (($includeinternet==0)||($transactionresult=="success"))){
	
	$commentid=$comment[name];
            
		##post a comment reply
		print "<br>submitting a reply";
		mysql_query("INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp) 
	VALUES ('', 'comment', '$commentid', '', '$reply', '', '', '0', '".time()."')",$con);

	}

;
	if ( ( ($transactionresult=="fail" && $includeflip==0) || $tiptype=="message") ){

	
	 $message="Transaction $rejectverify!\n\n$strikethrough**$tipsenderusername --> $tipbitcoinamount BTC *(~$$tipdollaramount USD)* --> $tipreceiver**$strikethrough\n\n$cancelmessage"."\n\n[About Bitcointip](http:##www.reddit.com/r/test/comments/11ei62/bitcointip_tip_redditors_with_bitcoin/)";
	
		##PM Sender
		if ($transactionresult=="success")
		$subject="Successful Bitcointip Notice";

		if ($transactionresult=="fail")
		$subject="Failed Bitcointip Notice";	
		
				print "<br>submitting a message";

		mysql_query("INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp) 
	VALUES ('', 'message', '$tipsenderusername', '$subject', '$message', '', '', '0', '".time()."')",$con);

	}


}

			
		
			
			




		
		
		
		
	}
	else
	{
		##/this comment contains no "+bitcointip" or a "+1 internet"
		
		##reserved for NerdfighterSean commands to the bot.

	}
	

}




#eval_comments
# get new comments and go through each one looking for a command, then respond.
def eval_comments():
	#TODO
	#get all the comments that haven't yet been gotten.
	
	#go through all those comments oldest to newest and do find_comment_command(commentdataarray) on each comment
	find_comment_command(commentdataarray)
	
	#then when done, log the last comment evaluated.
	# we'll start with that comment next time around.






#submit_messages
#submits outgoing messages/comments to reddit.com
def submit_messages():

	#go through each entry, and try to submit reply.
	#if reply is sent out, mark message as sent=1.
	#if reply is not sent because of error, mark as sent=x.

	stop = 0
	
	##go through list of tosubmit orderby timestamp from oldest to newest
	sql = "SELECT * FROM TEST_TABLE_TOSUBMIT WHERE sent='0' ORDER BY timestamp ASC"
	mysqlcursor.execute(sql)
	result = mysqlcursor.fetchall()
	for row in result:
		if (stop == 0):
			print ("Trying to go through each unsent message/comment")
			type = row[1]
			replyto = row[2]
			subject = row[3]
			text = row[4]
			captchaid = row[5]
			captchasol = row[6]
			sent = row[7]
			timestamp = row[8]
			
			print ("Type:", type)
			
			if ( type == "comment" ): 
				
				#try to post comment reply
				#comment = submission.comments[0] ?
				#comment.reply('test') ?
				
				#TODO
				#what is proper way to send a reply to a comment?
				#use praw here
				comment = make_comment_object( with thingid=replyto)
				sendresult = comment.reply(text)
				
				print ("Tried to send comment.")
				
				#TODO based on sendresult, mark message sent?
				if( sendresult == "sent"? ):
					##it worked.
					$sql = "UPDATE TEST_TABLE_TOSUBMIT SET sent=1 WHERE type='%s' AND timestamp='%d' AND replyto='%s'" % (type, timestamp, replyto)
					mysqlcursor.execute(sql)
					mysqlcon.commit()
					print ("Comment delivered")
					
				else if ( sendresult == "ratelimited"? ):
					##it wasn't sent
					print ("Not sent... stopping...")
					stop = 1
					
				else if ( sendresult == "error" ):
					$sql = "UPDATE TEST_TABLE_TOSUBMIT SET sent=x WHERE type='%s' AND timestamp='%d' AND replyto='%s'" % (type, timestamp, replyto)
					mysqlcursor.execute(sql)
					mysqlcon.commit()
					print ("Comment not sent because of error.")
				

			if ( type == "message" ): 
				
				#try to send a personal message
				
				#TODO
				#what is proper way to send a reply to a message and it's output?
				#use praw here
				sendresult = reddit.compose_message(replyto, subject, test)
				
				print ("Tried to send message.")
				
				#TODO based on sendresult, mark message sent?
				if( sendresult == "sent"? ):
					##it worked.
					$sql = "UPDATE TEST_TABLE_TOSUBMIT SET sent=1 WHERE type='%s' AND timestamp='%d' AND replyto='%s'" % (type, timestamp, replyto)
					mysqlcursor.execute(sql)
					mysqlcon.commit()
					print ("Message delivered")
					
				else if ( sendresult == "ratelimited"? ):
					##it wasn't sent
					print ("Not sent... stopping...")
					stop = 1
					
				else if ( sendresult == "error" ):
					#user doesn't exist or some other reason to cancel the message
					$sql = "UPDATE TEST_TABLE_TOSUBMIT SET sent=x WHERE type='%s' AND timestamp='%d' AND replyto='%s'" % (type, timestamp, replyto)
					mysqlcursor.execute(sql)
					mysqlcon.commit()
					print ("Message not sent because of error.")





######################################################################
#MAIN
######################################################################

#DECRYPT DETAILS FOR USE:
decMYSQLDBhost = decrypt(encMYSQLDBhost)
decMYSQLDBlogin = decrypt(encMYSQLDBlogin)
decMYSQLDBpass = decrypt(encMYSQLDBpass)
decMYSQLDBdbname = decrypt(encMYSQLDBdbname)
decBITCOINDlogin = decrypt(encBITCOINDlogin)
decBITCOINDpass = decrypt(encBITCOINDpass)
decBITCOINDip = decrypt(encBITCOINDip)
decBITCOINDport = decrypt(encBITCOINDport)
decBITCOINDsecondpass = decrypt(encBITCOINDsecondpass)
decREDDITbotusername = decrypt(encREDDITbotusername)
decREDDITbotpassword = decrypt(encREDDITbotpassword)
decREDDITbotid = decrypt(encREDDITbotid)

# CONNECT TO MYSQL DATABASE
mysqlcon = MySQLdb.connect(decMYSQLDBhost, decMYSQLDBlogin, decMYSQLDBpass, decMYSQLDBdbname)
mysqlcursor = mysqlcon.cursor()

# CONNECT TO BITCOIND SERVER
jsonRPCClientString = "http://"+decBITCOINlogin+":"+decBITCOINpass"+@"+decBITCOINDip+":"+decBITCOINDport+"/"
bitcoind.access = ServiceProxy(jsonRPCClientString)

# CONNECT TO REDDIT.COM
reddit = praw.Reddit(user_agent = "bitcointip bot by /u/nerdfightersean")
reddit.login(decredditbotusername, decredditbotpassword)


looping = 1
# WHILE THE BOT DOESN'T HAVE ANY PROBLEMS, KEEP LOOPING OVER EVALUATING COMMENTS, MESSAGES, AND SUBMITTING REPLIES
while(looping):
	#UNLOCK BITCOIND WALLET
	print "Unlocking Bitcoin Wallet..."
	print  (bitcoind.walletpassphrase(decBITCOINDsecondpass, 600))

	#CHECK/UPDATE EXCHANGE RATE
	print "Checking Exchange Rate..."
	exchangerate = getExchangeRate("mtgoxUSD")

	#CHECK FOR NEW REDDIT PERSONAL MESSAGES
	if (botstatus == "up"):
		print "Checking Messages..."
		eval_messages()

	#CHECK FOR NEW COMMENTS
	if (botstatus == "up"):
		print "Checking Comments..."
		eval_comments()

	#UPDATE PENDING TRANSACTIONS
	if (botstatus == "up"):
		print "Updating Pending Transactions..."
		update_transactions()
	
	#SUBMIT MESSAGES IN OUTBOX TO REDDIT
	if (botstatus == "up"):
		print "Submitting Messages and comment replies..."
		submit_messages()

	#LOCK BITCOIND WALLET
	if (botstatus == "up"):
		print "Locking Bitcoin Wallet"
		print (bitcoind.walletlock())
	
#LOCK BITCOIND WALLET AT PROGRAM END
print "Locking Bitcoin Wallet"
print (bitcoind.walletlock())