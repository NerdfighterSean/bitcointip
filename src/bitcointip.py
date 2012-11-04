#reddit api wrapper
import praw

#import encryption/decryption stuff
import rijndael
import base64

#bitcoindwrapper and custom methods
#txid = bitcoind.transact(fromthing, tothing, amount)
import bitcoind

#timestamp = time.time()
import time

#import mysql stuff
import MySQLdb

#datastring = urllib2.urlopen(url).read()
import urllib2

#jsonarray = json.loads(jsonstring)
#jsonstring = json.dumps(jsonarray)
import json

#regex stuff
import re

	

######################################################################
#SETTINGS AND OPTIONS
######################################################################
#Encrypt/Decrypt settings
KEY_SIZE = 16
BLOCK_SIZE = 32

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


# BANNED USERS
bannedusers = []

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

def encrypt(key, plaintext):
    padded_key = key.ljust(KEY_SIZE, '\0')
    padded_text = plaintext + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE) * '\0'

    # could also be one of
    #if len(plaintext) % BLOCK_SIZE != 0:
    #    padded_text = plaintext.ljust((len(plaintext) / BLOCK_SIZE) + 1 * BLOCKSIZE), '\0')
    # -OR-
    #padded_text = plaintext.ljust((len(plaintext) + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE)), '\0')

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    ciphertext = ''
    for start in range(0, len(padded_text), BLOCK_SIZE):
        ciphertext += r.encrypt(padded_text[start:start+BLOCK_SIZE])

    encoded = base64.b64encode(ciphertext)

    return encoded


def decrypt(key, encoded):
    padded_key = key.ljust(KEY_SIZE, '\0')

    ciphertext = base64.b64decode(encoded)

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    padded_text = ''
    for start in range(0, len(ciphertext), BLOCK_SIZE):
        padded_text += r.decrypt(ciphertext[start:start+BLOCK_SIZE])

    plaintext = padded_text.split('\x00', 1)[0]

    return plaintext
	
	
	
def getAllowedSubreddits():
	getreddits = reddit.user.my_reddits()
	for subreddit in getreddits:
		allowedsubreddits.append(subreddit.display_name.lower())
		print ("Got allowed subreddits:", allowedsubreddits)

		
def getFriends():

	#todo
	#get list of friends from mysql table.
	#friendsjson = tableentry
	#friendsarray = decode json
	friendsOfBitcointip = friendsarray


# GET THE EXCHANGE RATE FROM bitcoincharts.com
def getExchangeRate(symbol = "mtgoxUSD"):

	#if exchangeratetime is less than 3 hours ago, return the rate
	if ( ((time.time() - exchangeratelastupdated)<(updateexchangerateinterval)) ):
		return exchangerate

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
				print ("exchange rate updated to: ", exchangerate)
				return exchangerate
				
				
				

#subredditcheck
#if subreddit is in list of allowedsubreddits, return 1.
def subredditAllowed(subreddit):
	
	for (i, item) in enumerate(allowedsubreddits):
		if (item.lower() == subreddit.lower()):
			#subreddit allowed
			return 1

	#subreddit not allowed
	return 0

#userAllowed
#if a user is not in list of banned users, return 1.
def userAllowed(username):

	for (i, item) in enumerate(bannedusers):
		if (item.lower() == username.lower()):
			#user not allowed
			return 0

	#user allowed
	return 1

#addUser	
#add a user to the service and set them up with an address and account. returns "error" if unsuccessful.
def addUser(username):
	
	#create a deposit address for them
	newuseraddress = bitcoind.getnewaddress(username)
	if (newuseraddress == "error"):
		return "error"
	else:
		#add them to TABLE_USERS
		sql = "INSERT INTO TEST_TABLE_USERS (user_id, username, address, balance, datejoined) VALUES ('%s', '%s', '%s', '%f', '%d')" % ('', username, newuseraddress, 0.00000000, time())
		mysqlcursor.execute(sql)
		mysqlcon.commit()
		print ("User (%s) added with address (%s)") % (username, newuseraddress)



#update_lastactive
#update the user's lastactive time
def update_lastactive(username):

	#check if user has been active at all.  If so, update, if not insert.
	userhasbeenactive = 0
	
	sql = "SELECT * FROM TEST_TABLE_RECENT WHERE type='LASTACTIVE_%s'" % (username)
	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		userhasbeenactive = 1
	
	
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


#getUserBalance
#Get the current balance of a user. returns "error" if unsuccessful
def getUserBalance(username):

	userbalance = bitcoind.getbalance(username)
	
	if (userbalance != "error"):
		return userbalance
	else: 
		if (addUser(username) == "error"):
			return "error"	
	
	return getUserBalance(username)

#getUserAddress
#Get the current address of a user. returns "error" if unsuccessful
def getUserAddress(username):

	useraddress = bitcoind.getaddressesbyaccount(username)[0]

	if (useraddress != "error"):
		return useraddress
	else: 
		if (addUser(username) == "error"):
			return "error"	
	
	return getUserAddress(username)




#getUserGiftamount
#getUserGiftamount(username) get how much the user has donated to /u/bitcointip
def getUserGiftamount(username):

	sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='%s'" % (username)

	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		giftamount = row[5]
		return giftamount

	#if nothing was returned, the user doesn't exist yet. Add them. and try again.
	if (addUser(username) == "error"):
		return "error"
	
	return getUserGiftamount(username)



#hasUserRedeemedKarma
#checks to see if a user has gotten bitcoins from the reddit bitcoin faucet yet.
def hasUserRedeemedKarma(username):

	sql = "SELECT * FROM TEST_TABLE_FAUCET_PAYOUTS WHERE username='%s'" % (username)
	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		alreadyredeemed = 1
		
	if (alreadyredeemed == 1):
		print ("user has redeemed karma already.")
		return 1
	else:
		print ("user has not redeemed karma yet.")
		return 0


#doesTransactionExist
#double checks whether or not a transaction has already been done.
def doesTransactionExist(sender, receiver, timestamp):

	sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE sender_username='%s' AND receiver_username='%s' AND timestamp='%d'" % (sender, receiver, timestamp)
	mysqlcursor.execute(sql)
	results = mysqlcursor.fetchall()
	for row in results:
		#transaction already processed
		return 1
	
	#transaction doesn't exist.
	return 0

	
#create footer for the end of all PMs
def getFooter(username):
	footer = "\n\n---\n\n|||\n|:|:|\n| Account Owner: | **%s** |\n| Deposit Address: | **%s** |\n| Address Balance: | **%d BTC** *(~$%d USD)* \n|"."\n\n[About Bitcointip](http://www.reddit.com/r/bitcointip) (BETA!)" % (username, getUserAddress(username), getUserBalance(username), round(getUserBalance(username)*getExchangeRate("mtgoxUSD"),2))
	return footer
	
	
	
#doTransaction
#do the transaction
def doTransaction(transaction_from, transaction_to, transaction_amount, tip_type, tip_id, tip_subreddit, tip_timestamp):

	#returns success message or failure reason
	
	print ("doing transaction")
	
	#Search for transaction in transaction list to prevent double processing!
	if ( doesTransactionExist(transaction_from, transaction_to, tip_timestamp) == 1):
		print ("Transaction does already exist.")
		return ("cancelled")

	#submit the transaction to the wallet.
	txid = bitcoind.transact(transaction_from, transaction_to, transaction_amount)
	
	print ("txid: ", txid)
	
	#based on the statusmessage, set the status and process.
	if (txid != "error"):
		status = "pending"
		
		if (bitcoind.validateaddress(transaction_to)['isvalid'] == True):
			#we are sending to an address (not reversable)
			status = "completed"
	
		
		#do a transaction from sender to reciever for amount. put into TABLE_TRANSACTIONS
		sql = "INSERT INTO TEST_TABLE_TRANSACTIONS (transaction_id, sender_username, sender_address, receiver_username, receiver_address, amount_BTC, amount_USD, type, url, subreddit, timestamp, verify, statusmessage, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (txid, senderusername, senderaddress, receiverusername, receiveraddress, bitcoinamount, dollaramount, type, url, subreddit, timestamp, verify, statusmessage, status)
		mysqlcursor.execute(sql)
		mysqlcon.commit()
	
	
		#if tip is to bitcointip, add tip to giftamount for sender.
		if ( transaction_to.lower() == "bitcointip" ):
			oldgiftamount = getUserGiftamount(transaction_from)
			newgiftamount = oldgiftamount + transaction_amount
			sql = "UPDATE TEST_TABLE_USERS SET giftamount='%d' WHERE username='%s'" % (newgiftamount, transaction_from)
			mysqlcursor.execute(sql)
			mysqlcon.commit()
			
			#make all transactions to 'bitcointip' completed
			sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE receiver_username='bitcointip'" 
			mysqlcursor.execute(sql)
			mysqlcon.commit()
		
		print ("Transaction Successful")
		
	else:
		#(txid == "error") the transaction didn't go through right. and is canceled
		
		status = "cancelled"
		
		#even though canceled, enter into transaction list but as cancelled
		sql = "INSERT INTO TEST_TABLE_TRANSACTIONS (transaction_id, sender_username, sender_address, receiver_username, receiver_address, amount_BTC, amount_USD, type, url, subreddit, timestamp, verify, statusmessage, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (txid, transaction_from, 'null', transaction_to, 'null', transaction_amount, transaction_amount*getExchangeRate("mtgoxUSD"), tip_type, tip_id, tip_subreddit, tip_timestamp, 'null', 'null', status)
		mysqlcursor.execute(sql)
		mysqlcon.commit()
	
	#cancelled or pending
	
	#update lastactive for the sender because they are using tips
	update_lastactive(transaction_from)
	
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

	
	
	print ("Last Update Time:", lasttransactionsupdatedtimestamp)
		
		
	##do this once every day
	##if (transactiontime + 21days)< receiverlastactive, process the reversal of the transaction to the senders new address, and set transactionstatus=reversed.

	if ((lasttransactionsupdatedtimestamp+(updatetransactionsinterval)) <= time.time()):
		##if the transactions haven't been updated in 1 day, do the update.
	
		sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE status='pending'"

		mysqlcursor.execute(sql)
		results = mysqlcursor.fetchall()
		for row in results:
			transactionid = row[0]
			receiver = row[3]
			sender = row[1]
			timestamp = row[10]
			transactionamount = row[5]
			
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
				receiverbalance = getUserBalance(receiver)
				if (receiverbalance >= (transactionamount))
					##the receiver has enough, just move the coins from the receiveraddress back to the new senderaddress
					reversalamount = transactionamount - 0.0005
					
					reversalstatus = bitcoind.transact(receiver, sender, reversalamount)
					
					##mark the transaction as reversed in the table
					if(reversalstatus != "error"):
						sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='reversed' WHERE transaction_id='%s'" % (transactionid)
						mysqlcursor.execute(sql)
						mysqlcon.commit()
						print ("Transaction reversed: ", transactionid)
					else:
						##the user doesn't have enough to reverse the transaction, they must have spent it in another way.
						sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s'" % (transactionid)
						mysqlcursor.execute(sql)
						mysqlcon.commit()
						print ("Transaction completed (user already spent funds):", transactionid)
				else:
					## the receiver doesn't have enough.  They must have already spent it
					##mark as completed instead of reversed.
					sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s'" % (transactionid)
					mysqlcursor.execute(sql)
					mysqlcon.commit()
					print ("Transaction completed (user already spent funds):", transactionid)
			

		
		
		#Get ready to send out weekly notifications to users who have pending transactions to them that they need to accept.
		##get TRANSACTIONS_NOTIFIED timestamp from TEST_TABLE_RECENT
		sql = "SELECT * FROM TEST_TABLE_RECENT WHERE type='TRANSACTIONS_NOTIFIED'"
		mysqlcursor.execute(sql)
		results = mysqlcursor.fetchall()
		for row in results:
			lasttransactionsnotifiedtimestamp = row[1]
			print ("Last Notify Time:", lasttransactionsnotifiedtimestamp)
		
		
	
		
		##do notifications weekly, not daily.
		if ((lasttransactionsnotifiedtimestamp+(notifytransactionsinterval)) <= time.time()):
			print ("<br><br>Going through each user to see if need to notify")
	
			##go through each user and compile list of pending transactions to them.
			sql = "SELECT * FROM TEST_TABLE_USERS WHERE 1"
			mysqlcursor.execute(sql)
			result = mysqlcursor.fetchall()
			for row in result:
				username = row[1]
				havependingtransaction = 0
				
				sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE receiver_username='%s' AND status='pending' ORDER BY timestamp ASC" % (username)
				mysqlcursor.execute(sql)
				resultb = mysqlcursor.fetchall()
				for row in resultb:
					havependingtransaction = 1
					oldesttransaction = row[10]
			
				if (havependingtransaction == 1)
				
					print (username, " has a pending transaction")
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
							sender = row[1]
							receiver_username = row[3]
							receiver_address = row[4]
							amount_BTC = row[5]
							amount_USD = row[6]
							status = row[13]
							timestamp = row[10]
							
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
						k += 1
					
						
		
					transactionhistorymessage = transactionhistorymessage + "**Only includes tips to or from your Reddit username.*\n\n"
		
					message = message + transactionhistorymessage
				
					#add footer
					message = message + getFooter(username)
				
					##put message in to submit table
					sql = "INSERT INTO TEST_TABLE_TOSUBMIT (type, replyto, subject, text, captchaid, captchasol, sent, timestamp) VALUES ('message', '%s', 'Bitcointip Pending Transaction(s) Notice', '%s', '', '', '0', '%d')" % (username, message, time.time())
					mysqlcursor.execute(sql)
					mysqlcon.commit()
				
					print ("<br><br>Notification of Pending transactions prepared for $username")
					
				
		
			if (lasttransactionsnotifiedtimestamp == 0):
				##if listing doesn't exist, insert
				sql = "INSERT INTO TEST_TABLE_RECENT (type,timestamp) values('TRANSACTIONS_NOTIFIED', '%d')" % (time.time())
				mysqlcursor.execute(sql)
				mysqlcon.commit()
				print ("<br><br>TRANSACTIONS_INSERTED(NOTIFIED) to ")
				
			else:
				
				##else update
				sql = "UPDATE TEST_TABLE_RECENT SET timestamp='%d' WHERE type='TRANSACTIONS_NOTIFIED'" % (time.time())
				mysqlcursor.execute(sql)
				mysqlcon.commit()
				print ("<br><br>TRANSACTIONS_UPDATED(NOTIFIED) to ")
				
			
		else:
		
			print "Not time to send notifications yet.";
			
	
	
	
	
	
		##update TRANSACTIONS_UPDATED timestamp from TEST_TABLE_RECENT to time()
		if (lasttransactionsupdatedtimestamp == 0):
			##if listing doesn't exist, insert
			sql = "INSERT INTO TEST_TABLE_RECENT (type,timestamp) values('TRANSACTIONS_UPDATED', '"%d"')" % (time.time())
			mysqlcursor.execute(sql)
			mysqlcon.commit()
			print ("<br><br>TRANSACTIONS_INSERTED(UPDATED) to ")
			
		else:
			##else update
			sql = "UPDATE TEST_TABLE_RECENT SET timestamp='%d' WHERE type='TRANSACTIONS_UPDATED'" % (time.time())
			mysqlcursor.execute(sql)
			mysqlcon.commit()
			print ("<br><br>TRANSACTIONS_UPDATED(UPDATED) to ")
	else:
		print ("<br><br> Hasn't beena day yet.")
	

	
def eval_tip(thing):
	#evaluates a user tip, does the tip if valid, and then sends comment reply and messages if needed
	
	#See if the message author has a bitcointip account, if not, ignore them.  Must send PM to bot to sign up.
	sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='%s'" % (thing.author.name)
	mysqlcursor.execute(sql)
	result = mysqlcursor.fetchall()
	for row in result:
		userhasaccount = 1

	if (userhasaccount == 0)
		return 0
	
	##List all the properties the tip could have
	tip_senderusername = thing.author.name
	tip_timestamp = thing.created_utc
	tip_id = thing.name
	tip_subreddit = thing.subreddit.name
	tip_type = #message or comment? todo
	if (thing.dest=="bitcointip"):
		tip_type = "message"
	else:
		tip_type = "comment"
	
	#Now get the properties of the tip string
	##isolate the tipping command
	regex_start_string = "(\+((bitcointip)|(bitcoin)|(tip)|(btctip)|(bittip)|(btc)))" #start tip
	regex_bitcoinaddress_string = "(1([A-Za-z0-9]{25,35}))" #bitcoin address
	regex_redditusername_string = "((@)?([A-Za-z0-9_-]{3,20}))" #reddit username
	regex_fiatamount_string = "((((\$)?(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD))|(((\$)(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))(( )?USD)?))" #fiat amount
	regex_bitcoinamount_string = "(((((B)|(&bitcoin;))(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC)?)|(((B)|(&bitcoin;))?(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))(( )?BTC))))" #bitcoin amount
	regex_all_string = "(\bALL\b)" #all keyword
	regex_flip_string = "(\bFLIP\b)" #flip keyword
	regex_verify_string = "(\bNOVERIFY\b)" #noverify keyword
	regex_internet_string = "(\+1 internet(s)?)" #internet keyword
	
	# todo why doesn't this work? too large?
	#total=(((\+((bitcointip)|(bitcoin)|(tip)|(btctip)|(bittip)|(btc)))(\ )((1([A-Za-z0-9]{25,35}))|((@)?([A-Za-z0-9_-]{3,20})))?(\ )(((((\$)?(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))((\ )?USD))|(((\$)(((\d{1,3}(\,\d{3})*|(\d+))(\.\d{1,2})?)|(\.\d{1,2})))((\ )?USD)?))|(((((B)|(&bitcoin;))(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))((\ )?BTC)?)|(((B)|(&bitcoin;))?(((\d{1,3}(\,\d{3}){1,2}|(\d+))(((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8})))?))|((((\.)(((\d{3}\,\d{3}\,\d{1,2})|(\d{3}\,\d{1,3}))|(\d{1,8}))))))((\ )?BTC))))|(\bALL\b)|(\bFLIP\b))(\ )((\bNOVERIFY\b))?)|((\+1\ internet(s)?)))
	

	#((start (bitcoinaddress|redditusername)? (fiatamount|bitcoinamount|all|flip) (verify)?)|(internet))
	regex_tip_string = "(("+regex_start_string+" ("+regex_bitcoinaddress_string+"|"+regex_redditusername_string+")? ("+regex_fiatamount_string+"|"+regex_bitcoinamount_string+"|"+regex_all_string+"|"+regex_flip_string+") ("+regex_verify_string+")?)|("+regex_internet_string+"))"
	
	regex_start = re.compile(regex_start_string,re.IGNORECASE)
	regex_bitcoinaddress = re.compile(regex_bitcoinaddress_string,re.IGNORECASE)
	regex_redditusername = re.compile(regex_redditusername_string,re.IGNORECASE)
	regex_fiatamount = re.compile(regex_fiatamount_string,re.IGNORECASE)
	regex_bitcoinamount = re.compile(regex_bitcoinamount_string,re.IGNORECASE)
	regex_all = re.compile(regex_all_string,re.IGNORECASE)
	regex_flip = re.compile(regex_flip_string,re.IGNORECASE)
	regex_verify = re.compile(regex_verify_string,re.IGNORECASE)
	regex_internet = re.compile(regex_internet_string,re.IGNORECASE)
	regex_tip = re.compile(regex_tip_string,re.IGNORECASE)
	
	#isolate the tip_command from the text body
	tip_command = regex_tip.search(thing.body).groups(0)
	
	tip_command_start = regex_start.search(tip_command).groups(0)
	tip_command_bitcoinaddress = regex_bitcoinaddress.search(tip_command).groups(0)
	tip_command_redditusername = regex_redditusername.search(tip_command).groups(0)
	tip_command_fiatamount = regex_fiatamount.search(tip_command).groups(0)
	tip_command_bitcoinamount = regex_bitcoinamount.search(tip_command).groups(0)
	tip_command_all = regex_all.search(tip_command).groups(0)
	tip_command_flip = regex_flip.search(tip_command).groups(0)
	tip_command_verify = regex_verify.search(tip_command).groups(0)
	tip_command_internet = regex_internet.search(tip_command).groups(0)
	
	##Make sure all these values are filled by the time we get to the end:
	#transaction_from
	#transaction_to
	#transaction_amount
	
	#get transaction_from
	transaction_from = tip_senderusername
	
	#get transaction_to
	if (tip_command_redditusername):
		transaction_to = tip_command_redditusername.strip('@')
	else if (tip_command_bitcoinaddress):
		transaction_to = tip_command_bitcoinaddress
	else if (tip_type == "comment"):
		#recipient not specified
		#get author of parent comment
		transaction_to = #author of parent comment #todo use praw
	else if (tip_type == "message"):
		#malformed tip
		#must include recipient
		#error
		cancelmessage = "You must specify a recipient username or bitcoinaddress."
		
	
	#get transaction_amount
	if (tip_command_bitcoinamount):
		transaction_amount = tip_command_bitcoinamount.strip('B &bitcoin; btc BTC')
	else if (tip_command_fiatamount):
		transaction_amount = (float(tip_command_fiatamount.strip('$ usd USD'))/getExchangeRate("mtgoxUSD"))
	else if (tip_command_all):
			senderbalance = getUserBalance(transaction_from)
			transaction_amount = (senderbalance - 0.0005)
			transaction_amount = round(amount, 8)
	else if (tip_command_flip):
		if (getUserBalance(transaction_from)>=0.0105):
			if (getUserGiftamount(transaction_from)>=0.25):
				##do a coin flip
				flipresult = round(rand(0,1))
				if (flipresult==1):
					transaction_amount = 0.01
				else:
					transaction_amount = 0
			else:
				#error: not donated enough
				cancelmessage = "You have not donated enough to use the flip command."
		else:
			#error: not enough balance
			cancelmessage = "You don't have a bitcent (and fee) to flip."
	else if (tip_command_internet):
		if (getUserGiftamount(transaction_from)>=1):
			if (tip_command_internet.find('s')):
				transaction_amount = 0.02
				if (getUserBalance(transaction_from)<0.0205):
					cancelmessage = "You don't have 2 internets to give)
			else:
				if (getUserBalance(transaction_from)>=0.0105):
					transaction_amount = 0.01
		else:
		#error: not donated enough
		cancelmessage = "You have not donated enough to use the '+1 internet' command."
		
		
	##check conditions to cancel the transaction and return error message
	if (transaction_amount<=0 and !tip_command_flip and cancelmessage==""):
		cancelmessage = "You cannot send an amount <= 0. That is just silly."
	else if (transaction_amount+0.0005 > getUserBalance(transaction_from) and cancelmessage==""):
		cancelmessage = "You do not have enough in your account.  You have %d BTC, but need %d BTC (do not forget about the 0.0005 BTC fee per transaction)." % (getUserBalance(transaction_from), transaction_amount+0.0005)
	else if ( tip_type=="comment" and (subredditAllowed(tip_subreddit)==0) and (getUserGiftamount(transaction_from)<2) and cancelmessage==""):
		cancelmessage = "The %s subreddit is not currently supported for you." % (tip_subreddit)
	else if (userAllowed(transaction_from)==0 and tipsenderusername!="" and cancelmessage==""):
		cancelmessage="You are not allowed to send or receive money."
	else if (userAllowed(transaction_to)==0 and tipreceiverusername!="" and cancelmessage==""){
		cancelmessage="The user %s is not allowed to send or receive money." % (transaction_to)
	else if (transaction_to == transaction_from and cancelmessage==""):
		cancelmessage="You cannot send any amount to yourself, that is just silly."
	else if (transaction_to == "" and cancelmessage==""):
		cancelmessage="You must specify a recipient username or bitcoin address."

	if (!cancelmessage):
		transaction_status = doTransaction(transaction_from, transaction_to, transaction_amount, tip_type, tip_id, tip_subreddit, tip_timestamp)
		#todo, simplify doTransaction
	
	#based on the variables, form messages.
	verifiedmessage = "[*%s &nbsp; >>>> &nbsp; %d BTC (~$%d) &nbsp; >>>> &nbsp; %s*](http://reddit.com/r/bitcointip)" % (transaction_from, transaction_amount, round(transaction_amount*getExchangeRate("mtgoxUSD"), 2), transaction_to)
	
	rejectedmessage = "[~~*%s &nbsp; >>>> &nbsp; %d BTC (~$%d) &nbsp; >>>> &nbsp; %s*~~](http://reddit.com/r/bitcointip)" % (transaction_from, transaction_amount, round(transaction_amount*getExchangeRate("mtgoxUSD"), 2), transaction_to)
	
	#create special response for flip
	if (tip_command_flip and cancelmessage==""):
		if (flipresult==1):
			flipmessage = "Bit landed **1** up. %s wins 1 bitcent.\n\n" % (transaction_to)
		if (flipresult==0):
			flipmessage = "Bit landed **0** up. %s wins nothing.\n\n" % (transaction_to)
	else:
		flipmessage = ""
	
	#Reply to a comment under what conditions?
	#reply to a flip only if cancelmessage!="" 
	#reply to a +1 internet only if it is a success
	if (tip_type == "comment" and tip_command_verify.lower()!="noverify" and ((subredditAllowed(tip_subreddit)==1) or (getUserGiftamount(transaction_from)>=2))):
		#Reply to the comment
		if (transaction_status=="completed" or transaction_status=="pending"):
			commentreplymessage = flipmessage
			if (flipresult==1 or !tip_command_flip):
				commentreplymessage += verifiedmessage
		else:
		commentreplymessage += rejectedmessage
		
	if (commentreplymessage):
		#if comment reply is prepared, send it
		#enter reply into table todo
		
		
	
	#Send a message to the sender under what conditions?
	#if flipping, only send a pm to sender if they don't have enough for a flip.
	#if +1internet, do not send a pm to sender under any circumstance. (nonusers may use this without intent to tip, don't bother them)
	if (tip_type == "message" or transaction_status == "cancelled" or cancelledmessage):
		#PM the Sender
		if (transaction_status=="completed" or transaction_status=="pending"):
			pmsendersubject = "Successful Bitcointip Notice"
			pmsendermessage = flipmessage + verifiedmessage
		else:
			pmsendersubject = "Failed Bitcointip Notice"
			pmsendermessage = flipmessage + rejectedmessage
		#add footer to PM
		pmsendermessage += getFooter(transaction_from)
	
	if (pmsendermessage):
		#if pm to sender is prepared, send it
		#enter message into table todo
	
	#Send a message to the receiver under what conditions?
	#only PM receiver if tip_type is a message and success
	if (tip_type == "message" and transaction_status == "pending"):
		#PM the Receiver
		pmreceiversubject = "Successful Bitcointip Notice"
		pmreceivermessage = flipmessage +verifiedmessage 
		
		#add footer to PM
		pmreceivermessage += getFooter(transaction_to)
		
	if (pmreceivermessage):
		#if pm to receiver is prepared, send it
		#enter message into table todo
			
	if (tip_command):
		#tip found and done
		return 1
	else:
		#no tip in this text
		return 0

	
#find_message_command
#returns text result as message to send back.
def find_message_command(message): #array
	
	
	if (botstatus == "down")
		#if down, just reply with a down message to all messages
		returnstring "The bitcointip bot is currently down.\n\n[Click here for more information about the bot.](http://www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/)\n\n[Click here for more information about bitcoin.](http://www.weusecoins.com/)\n\n[Click here to get a bitcoin wallet.](https://blockchain.info/wallet/)"
		return returnstring
	
	userhasaccount = 0
	#See if the message author has a bitcointip account, if not, make one for them.
	sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='%s'" % (message.author.name)
	mysqlcursor.execute(sql)
	result = mysqlcursor.fetchall()
	for row in result:
		userhasaccount = 1

	if (userhasaccount == 0)
		addUser(message.author.name)
	
	
	#Start going through the message for commands. Only the first found will be evaluated
	
	
	#"REDEEM KARMA: 1thisisabitcoinaddresshereyes"
	#if bitcoinaddress is valid, 
	regex_karmaredeem = re.compile("REDEEM( )?KARMA:( )?(1([A-Za-z0-9]{25,35}))",re.IGNORECASE)
	command_karmaredeem = regex_karmaredeem.search(message.body)
	
	if (command_karmaredeem and returnstring==""):
		
		#karma redemption command found
		karmabitcoinaddress = command_karmaredeem.groups(2)
		
		#karma limits on which redditors can get bitcoins for their karma
		minlinkkarma = 0
		mincommentkarma = 200
		mintotalkarma = 200

		#baseline amount of bitcoin to give each redditor (enough to cover some mining fees)
		defaultbitcoinamount = 0.00200000


		#get balance of bitcoinfaucet
		faucetbalance = getUserBalance("bitcointipfaucetdepositaddress")
		
		
		
		if ( hasUserRedeemedKarma(message.author.name) == 0 ):
			#if not redeemed yet, check for a valid bitcoin address

			print ("user has not redeemed karma yet.")

			if ( bitcoind.validateaddress(karmabitcoinaddress) == 1 ):
			
				#valid bitcoin address detected

				#get user's link karma and comment karms
				print ("Valid bitcoin address detected: ", karmabitcoinaddress)
				
		
				
	
				linkkarma = message.author.link_karma
				commentkarma = message.author.comment_karma
				totalkarma = linkkarma + commentkarma
	
				

				#format all the bitcoin amounts correctly for messages and displaying and storage
				
				#calculate how many bitcoins they might get from karma
				karmabitcoinamount = round((totalkarma/(100000000)),8)
				#print "bitcoin amount: ".number_format($karmabitcoinamount, 8, ".", "");
				
				#only give valid reddit users any bitcoins (check that karma is above a certain amount)
				if ( linkkarma>minlinkkarma and commentkarma>mincommentkarma and totalkarma>mintotalkarma):
					#User has enough karma
					print ("user has enough karma")
					
					if ( karmabitcoinamount < 0.002 )
						 bitcoinamount = karmabitcoinamount +defaultbitcoinamount
						print ("give user defualt amount too.")
					else:
						bitcoinamount = karmabitcoinamount
						print ("don't give user default amount.")
					
					#check to make sure the faucet has enough.
					if ( faucetbalance > (bitcoinamount+0.0005) ):
						
						#The reddit bitcoin faucet has enough
						print ("the reddit bitcoin faucet has: $faucetbalance.")

						#go ahead and send the bitcoins to the user
						txid = bitcoind.transact("bitcointipfaucetdepositaddress", karmabitcoinaddress, bitcoinamount)

						if (txid != "error"):
							print ("no error, transaction done, bitcoins en route.")
							#reply to their message with success
							returnstring = "Your bitcoins are on their way.  Check the status here: http://blockchain.info/address/%s\n\nIf you do not want your bitcoins, consider donating them to a [good cause](https://en.bitcoin.it/wiki/Donation-accepting_organizations_and_projects)." % (karmabitcoinaddress)
							
							#insert the transaction to the list of TABLE_FAUCET_PAYOUTS
							sql = "INSERT INTO TEST_TABLE_FAUCET_PAYOUTS (transaction_id, username, address, amount, timestamp) VALUES ('%s', '%s', '%s', '%d', '%d')" % (txid, message.author.name, karmabitcoinaddress, bitcoinamount, time.time())
							mysqlcursor.execute(sql)
							mysqlcon.commit()

						else:
							#there was an error with blockchain, have the user try again later maybe.
							print ("error with the bitcoind.")
							#say so.
							returnstring = "The Reddit Bitcoin Faucet is down temporarily.  Try again another day."

					else:
						#faucet is out of bitcoins.
						#say so.
						returnstring = "The Reddit Bitcoin Faucet is out of bitcoins until someone donates more. View the balance [here](http://blockchain.info/address/13x9weHkPTFL2TogQJz7LbpEsvpQJ1dxfa)."
					
				else:

					#user doesn't have enough karma
					print ("User doesn't have enough karma.")
					returnstring = "You do not have enough karma to get bitcoins. You need at least mincommentkarma Comment Karma to be eligible (You only have commentkarma). Keep redditing or try this bitcoin faucet: https://freebitcoins.appspot.com" % (mincommentkarma, commentkarma)

			else:
				#no valid bitcoin address detected
				print ("No valid bitcon address detected.")
				returnstring = "No valid bitcoin address detected.  Send the string \"REDEEM KARMA: 1YourBitcoinAddressHere\" please."

		else:
			print ("User has already redeemed karma")
			#user has already redeemed karma, can't do it again.
			returnstring = "You have already sold your karma for bitcoins.  You can only do this once."
	
	
	#"TRANSACTIONS"/"HISTORY"/"ACTIVITY"
	#Gives use a list of their transactions including deposits/withdrawals/sent/recieved
	regex_history = re.compile("((TRANSACTIONS)|(HISTORY)|(ACTIVITY))",re.IGNORECASE)
	command_history = regex_history.search(message.body)
	
	if (command_history and returnstring==""):
		
		#add first line of transaction table headers to the response.
		transactionhistorymessage = "\n#**%s Transaction History***\n\nDate | Sender | Receiver | BTC | ~USD | Status |\n|:|:|:|:|:|:|\n" % (message.author.name)
		k = 0

		sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE sender_username='%s' OR receiver_username='%s' ORDER BY timestamp DESC" % (message.author.name, message.author.name)
		mysqlcursor.execute(sql)
		result = mysqlcursor.fetchall()
		for row in result:
			if (k<11):
				sender = row[1]
				receiver_username = row[3]
				receiver_address = row[4]
				amount_BTC = row[5]
				amount_USD = row[6]
				status = row[13]
				timestamp = row[10]
				
				##if tip is sent directly to address with no username, display address.
				if (receiver_username == ""):
					receiver = receiver_address
				else:
					receiver = receiver_username
				
				date = date("D M d, Y", $timestamp);#todo python
				
				
				if (sender == message.author.name):
					senderbold = "**"
					amountsign = "*"
				else if (receiver == message.author.name):
					receiverbold = "**"
					amountsign = "**"
					
				##add new transaction row to table being given to user
				newrow = "| %s | %s%s%s | %s%s%s | %s%s%s | %s$%s%s | %s |\n" % (date, senderbold, sender, senderbold, receiverbold, receiver, receiverbold, amountsign, amount_BTC, amountsign, amountsign, amount_USD, amountsign, status)
				transactionhistorymessage = transactionhistorymessage + newrow

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
	
	regex_importkey = re.compile("((REPLACE PRIVATE KEY WITH:)( )?(5[a-zA-Z0-9]{35,60})(( )*(\n)*( )*)(TRANSFER BALANCE:)( )?(Y|N))",re.IGNORECASE)
	command_importkey = regex_importkey.search(message.body)
	
	if (command_importkey and returnstring==""):

		if (getUserGiftamount(message.author.name) >= 0.5):
		#do it
		
			print ("<br>Private Key detected...")
			privatekey = command_importkey.groups(3)
			transfer = command_importkey.groups(10)
			
			print ("Private Key: XXXXX")
			print ("Transfer: ", transfer)
			
			authoroldaddress = getUserAddress(message.author.name)
			authoroldbalance = getUserBalance(message.author.name)
			
			print ("authoroldaddress: ", authoroldaddress)
			print ("authoroldbalance: ", authoroldbalance)
			
			
			
			
			importstatus = (bitcoind.importprivkey(privatekey, "thisisatemporarylabelthatnobodyshoulduse"))
			
			print ("importstatus: ", importstatus)
			
				if (importstatus == true):
			
				authornewaddress = bitcoind.getaddressesbyaccount("thisisatemporarylabelthatnobodyshoulduse")[0]
				authornewbalance = bitcoind.getbalance("thisisatemporarylabelthatnobodyshoulduse")
				
				print ("authornewaddress: ", authornewaddress)
				print ("authornewbalance: ", authornewbalance)
			
				setaccountold = bitcoind.setaccount(authoroldaddress, "OLD ADDRESS: "+message.author.name)
				setaccountnew = bitcoind.setaccount(authornewaddress, message.author.name)
				
				print ("setaccountold: ", setaccountold)
				print ("setaccountnew: ", setaccountnew)
				
				
				if (setaccountold == true and setaccountnew == true):
				
					returnstring = "Replacement successful. Your new bitcoin address is: %s.\n\nYour old bitcoin address was: ~~%s~~." % (authornewaddress, authoroldaddress)
				if (transfer.lower() == "y" and authoroldbalance != 0):
					moveamount = authoroldbalance - 0.0005
					movedstatus = bitcoind.transact(authoroldaddress, authornewaddress, moveamount) 
					print ("movedstatus: ", movedstatus)
					if (movedstatus != "error"):
						returnstring += "\n\nYour old balance of %s is being moved to your new address." % (moveamount)
						authornewbalance += moveamount
					else	
						returnstring += "\n\nThere was a problem moving your funds. Either you have too little or something went wrong."
			
				##update user table entry with new balance and new address

				sql = "UPDATE TEST_TABLE_USERS SET address='%s' WHERE username='%s'" % (authornewaddress, message.author.name)
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
	regex_accept = re.compile("(ACCEPT)",re.IGNORECASE)
	command_accept = regex_accept.search(message.body)
	
	if (command_accept and returnstring==""):
		update_lastactive(message.author.name);
		returnstring = "All pending transactions will be accepted.  No currently existing tips to you will be reversed."
	

	
	##CHECK FOR MESSAGE TIP (take care of sending all messages here, return empty string, telling eval_messages to not send any more messages.
	
	if (eval_tip(message)==1)
		#if returns 1, then a tip was found.
		#only do one command per message, so stop looking for more commands
		#messages sent in eval_tip.
		return ""
		
		
		
	##HELP
	regex_help = re.compile("(HELP)",re.IGNORECASE)
	command_help = regex_help.search(message.body)
	
	if (command and returnstring==""):
		returnstring = "Check the [Help Page](http://www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/)."
		
		
	##NO COMMAND FOUND DO YOU NEED HELP?
	if (returnstring == ""):	
		returnstring = "This is the bitcointip bot.  No command was found in your message.\n\nTo fund your account, send bitcoins to your Deposit Address.\n\nFor help with commands, see [This Page](http://www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/).\n\n*Replies from the bot take on average 7.5 minutes but may take 30 minutes or more in some cases.*\n\n*Deposits are updated once per hour.*"
		
		

	##ALL MESSAGES ADD FOOTER TO END OF ANY MESSAGE
		
	returnstring += getFooter(message.author.name)

		
	##return returnstring;
	
	#insert returnstring into TEST_TABLE_TOSUBMIT
	#todo
	
	}





#eval_messages
#get new messages and go through each one looking for a command, then respond.
def eval_messages():
	#get some unread messages.
	unread_messages = reddit.user.get_unread(limit=1000)
	for message in unread_messages:
		if (message.was_comment == False):
			if (message.author.name != "bitcointip"):
					#check message for command
					find_message_command(message)
					#mark as read
					message.mark_as_read()


#find_comment_command
#find a command in a user comment
def find_comment_command(comment):
	eval_tip(comment)




#eval_comments
# get new comments and go through each one looking for a command, then respond.
def eval_comments():
	multiredditstring = ""
	for x in allowedsubreddits:
		multiredditstring += x + "+"
	
	multi_reddits = reddit.get_subreddit(multiredditstring)
	
	#go through comments of allowed subreddits
	
	lastcommentevaluatedtimestamp = #todo get from mysql table
	
	first_comment_this_loop = None
	print ("checking")
	multi_reddits_comments = multi_reddits.get_comments(limit=1000)
	for comment in multi_reddits_comments:
		if not first_comment_this_loop:
			first_comment_this_loop = comment.created_utc
		if comment.created_utc <= lastcommentevaluatedtimestamp:
			print ("old comment")
			break
		else:
			if (comment.author.name not in friendsOfBitcointip):#exclude friendsofbitcointip
				#print ("(",comment.subreddit,")",comment.author,":",comment.body)
				find_comment_command(comment)
	lastcommentevaluatedtimestamp = first_comment_this_loop
	#todo, write updated lastcommentevaluatedtimestamp to table.
		
	#now go through friendsofbitcointip
	
	friends_reddit = reddit.get_subreddit("friends")
	lastfriendcommentevaluatedtimestamp = #todo get from mysql table
	
	first_comment_this_loop = None
	print ("checking")
	friends_reddit_comments = friends_reddit.get_comments(limit=1000)
	for comment in friends_reddit_comments:
		if not first_comment_this_loop:
			first_comment_this_loop = comment.created_utc
		if comment.created_utc <= lastfriendcommentevaluatedtimestamp:
			print ("old comment")
			break
		else:
			#print ("(",comment.subreddit,")",comment.author,":",comment.body)
			find_comment_command(comment)
	lastfriendcommentevaluatedtimestamp = first_comment_this_loop
	#todo, write updated lastfriendcommentevaluatedtimestamp to table.


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
decMYSQLDBhost = decrypt(decryptionkey, encMYSQLDBhost)
decMYSQLDBlogin = decrypt(decryptionkey, encMYSQLDBlogin)
decMYSQLDBpass = decrypt(decryptionkey, encMYSQLDBpass)
decMYSQLDBdbname = decrypt(decryptionkey, encMYSQLDBdbname)
decBITCOINDlogin = decrypt(decryptionkey, encBITCOINDlogin)
decBITCOINDpass = decrypt(decryptionkey, encBITCOINDpass)
decBITCOINDip = decrypt(decryptionkey, encBITCOINDip)
decBITCOINDport = decrypt(decryptionkey, encBITCOINDport)
decBITCOINDsecondpass = decrypt(decryptionkey, encBITCOINDsecondpass)
decREDDITbotusername = decrypt(decryptionkey, encREDDITbotusername)
decREDDITbotpassword = decrypt(decryptionkey, encREDDITbotpassword)
decREDDITbotid = decrypt(decryptionkey, encREDDITbotid)

# CONNECT TO MYSQL DATABASE
mysqlcon = MySQLdb.connect(decMYSQLDBhost, decMYSQLDBlogin, decMYSQLDBpass, decMYSQLDBdbname)
mysqlcursor = mysqlcon.cursor()

# CONNECT TO BITCOIND SERVER
jsonRPCClientString = "http://"+decBITCOINlogin+":"+decBITCOINpass"+@"+decBITCOINDip+":"+decBITCOINDport+"/"
bitcoind.access = ServiceProxy(jsonRPCClientString)

# CONNECT TO REDDIT.COM
reddit = praw.Reddit(user_agent = "bitcointip bot by /u/nerdfightersean https://github.com/NerdfighterSean/bitcointip")
reddit.login(decREDDITbotusername, decREDDITbotpassword)

allowedsubreddits = []
getAllowedSubreddits()

friendsOfBitcointip = []
getFriendsOfBitcointip()

looping = 1
# WHILE THE BOT DOESN'T HAVE ANY PROBLEMS, KEEP LOOPING OVER EVALUATING COMMENTS, MESSAGES, AND SUBMITTING REPLIES
while(looping):
	#UNLOCK BITCOIND WALLET
	print "Unlocking Bitcoin Wallet..."
	print  (bitcoind.walletpassphrase(decBITCOINDsecondpass, 6000))

	#CHECK/UPDATE EXCHANGE RATE
	print "Checking Exchange Rate..."
	exchangerate = getExchangeRate("mtgoxUSD")

	#CHECK FOR NEW REDDIT PERSONAL MESSAGES
		print "Checking Messages..."
		eval_messages()

	#CHECK FOR NEW COMMENTS
	if (botstatus == "up"): #if down, don't check comments
		print "Checking Comments..."
		eval_comments()

	#UPDATE PENDING TRANSACTIONS
	if (botstatus == "up"): #if down, don't update pending transactions
		print "Updating Pending Transactions..."
		update_transactions()
	
	#SUBMIT MESSAGES IN OUTBOX TO REDDIT
		print "Submitting Messages and comment replies..."
		submit_messages()

	#LOCK BITCOIND WALLET
		print "Locking Bitcoin Wallet"
		print (bitcoind.walletlock())
	
#LOCK BITCOIND WALLET AT PROGRAM END
print "Locking Bitcoin Wallet"
print (bitcoind.walletlock())