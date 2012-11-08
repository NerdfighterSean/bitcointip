from decimal import Decimal

#python reddit api wrapper
import praw

#bitcoindwrapper and custom methods
#txid = bitcoind.transact(fromthing, tothing, amount)
import bitcoind

#jsonrpc
from jsonrpc import ServiceProxy

#timestamp = round(time.time())
import time

#mysql database stuff
import pymysql

#datastring = urllib.request.urlopen(url).read()
import urllib

#jsonarray = json.loads(jsonstring)

#jsonstring = json.dumps(jsonarray)
import json

#regex stuff
import re



#todo correct type handling when retrieving from table.
######################################################################
#FUNCTIONS
######################################################################
    
#function for updating the timestamp of the most recent thing done
def set_last_time(thingtype, value):

    #check if user has been active at all.  If so, update, if not insert.
    entryexists = False
    
    sql = "SELECT * FROM TEST_TABLE_RECENT WHERE type='%s'" % (thingtype)
    _mysqlcursor.execute(sql)
    results = _mysqlcursor.fetchall()
    for row in results:
        entryexists = True
    
    if (entryexists):
        #update username's lastactive time
        sql = "UPDATE TEST_TABLE_RECENT SET timestamp='%s' WHERE type='%s'" % (str(value), thingtype)
        _mysqlcursor.execute(sql)
        _mysqlcon.commit()
        print("Updated to MYSQL %s : %s" % (thingtype, str(value)))
    else:
        #insert username's lastactive time
        sql = "INSERT INTO TEST_TABLE_RECENT (type, timestamp) VALUES ('%s', '%s')" % (thingtype, str(value))
        _mysqlcursor.execute(sql)
        _mysqlcon.commit()
        print("Inserted to MYSQL %s : %s" % (thingtype, str(value)))

def get_last_time(thingtype):
    #return a timestamp
    value = 0
    sql = "SELECT * FROM TEST_TABLE_RECENT WHERE type='%s'" % (thingtype)
    _mysqlcursor.execute(sql)
    results = _mysqlcursor.fetchall()
    for row in results:
        value = row[1]
    print ("Retrieved from MYSQL %s : %s" % (thingtype, str(value)))

    try:
        value = int(value)
        return value
    except ValueError:
        try:
            value = json.dumps(value)
            return value
        except Exception:
            return value
    
    
#manage allowed subreddits by those subscribed to by user bitcointip
def refresh_allowed_subreddits():
    global _lastallowedsubredditsfetched
    global _lastallowedsubredditsfetchedtime
    _lastallowedsubredditsfetched = []
    getreddits = _reddit.user.my_reddits()
    for subreddit in getreddits:
        _lastallowedsubredditsfetched.append(subreddit.display_name.lower())
    print ("Retrieved from REDDIT allowed subreddits:", _lastallowedsubredditsfetched)
    _lastallowedsubredditsfetchedtime = round(time.time())
    set_last_time("lastallowedsubredditsfetchedtime",_lastallowedsubredditsfetchedtime)
    set_last_time("lastallowedsubredditsfetched",json.dumps(_lastallowedsubredditsfetched))

        
        
#manage friends by those that have flair on the bitcointip subreddit
def refresh_friends():
    global _lastfriendsofbitcointipfetched
    global _lastfriendsofbitcointipfetchedtime
    _lastfriendsofbitcointipfetched = []
    bitcointipsubreddit = _reddit.get_subreddit("bitcointip")
    bitcointipfriends = bitcointipsubreddit.flair_list()
    for x in bitcointipfriends:
        if (x['flair_css_class']=="bitcoin"):
            _lastfriendsofbitcointipfetched.append(x['user'].lower())
    print ("Retrieved from REDDIT friends of bitcointip:", _lastfriendsofbitcointipfetched)
    _lastfriendsofbitcointipfetchedtime = round(time.time())
    set_last_time("lastfriendsofbitcointipfetchedtime", _lastfriendsofbitcointipfetchedtime)
    set_last_time("lastfriendsofbitcointipfetched", json.dumps(_lastfriendsofbitcointipfetched))


        
#manage banned users by banned from bitcointip subreddit
def refresh_banned_users():
    global _lastbannedusersfetched
    global _lastbannedusersfetchedtime
    _lastbannedusersfetched = []
    bitcointipsubreddit = _reddit.get_subreddit("bitcointip")
    bitcointipbanned = bitcointipsubreddit.get_banned()
    for x in bitcointipbanned:
        _lastbannedusersfetched.append(x.name.lower())
    print ("Retrieved from REDDIT banned users:", _lastbannedusersfetched)
    _lastbannedusersfetchedtime = round(time.time())
    set_last_time("lastbannedusersfetchedtime", _lastbannedusersfetchedtime)
    set_last_time("lastbannedusersfetched", json.dumps(_lastbannedusersfetched))

# GET THE EXCHANGE RATE FROM bitcoincharts.com
#USD,AUD,CAD,EUR,JPY,GBP
def refresh_exchange_rate():

    print ("Checking Exchange Rate...")

    global _lastexchangeratefetched
    global _lastexchangeratefetchedtime
    
    exchangecode = "mtgox"
    ratetype = "avg"

    #if exchangeratetime is less than updatetime hours ago, do nothing
    if ( ((round(time.time()))<(_lastexchangeratefetchedtime + _intervalupdateexchangerate)) ):
        return ""

    #else if the timestamp is over updatetime hours old, update the exchangerates
    else:
        url = "http://bitcoincharts.com/t/markets.json"
        file = urllib.request.urlopen(url)
        encoding = file.headers.get_content_charset()
        content =file.readall().decode(encoding)
        jsondata = json.loads(content)

        for row in jsondata:
            for symbol in _lastexchangeratefetched.keys():
                if (row['symbol'] == (exchangecode+symbol)):
                    _lastexchangeratefetched[symbol] = row[ratetype]
                    _lastexchangeratefetched[symbol] = round(_lastexchangeratefetched[symbol],2)
                    print ("Exchangerate '" + symbol + "' updated to " + str(_lastexchangeratefetched[symbol]))
        _lastexchangeratefetchedtime = round(time.time())
        set_last_time("lastexchangeratefetchedtime", _lastexchangeratefetchedtime)
        set_last_time("lastexchangeratefetched", json.dumps(_lastexchangeratefetched))


#addUser    
#add a user to the service and set them up with an address and account. returns "error" if unsuccessful.
def add_user(username):

    #check to see if user already exists.
    useralreadyexists = False
    sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='%s'" % (username)
    _mysqlcursor.execute(sql)
    results = _mysqlcursor.fetchall()
    for row in results:
        useralreadyexists = True

    if (not useralreadyexists):
        #create a deposit address for them
        newuseraddress = bitcoind.getnewaddress(username)
        if (newuseraddress == "error"):
            return "error"
            print ("Error getting new user address for new user", username)
        else:
            #add them to TABLE_USERS
            sql = "INSERT INTO TEST_TABLE_USERS (user_id, username, address, balance, datejoined) VALUES ('%s', '%s', '%s', '%.8f', '%f')" % (None, username, newuseraddress, 0.00000000, round(time.time()))
            _mysqlcursor.execute(sql)
            _mysqlcon.commit()
            print ("User (%s) added with address (%s)" % (username, newuseraddress))


#getUserBalance
#Get the current balance of a user. returns "error" if unsuccessful
def get_user_balance(username):

    #if not user, add user
    add_user(username)
    
    userbalance = bitcoind.getbalance(username)
    
    if (userbalance != "error"):
        return float(userbalance)
    else: 
        if (add_user(username) == "error"):
            return "error"  
        else:
            return get_user_balance(username)

#getUserAddress
#Get the current address of a user. returns "error" if unsuccessful
def get_user_address(username):

    #if not user, add user
    add_user(username)

    useraddress = bitcoind.getaddressesbyaccount(username)[0]

    if (useraddress != "error"):
        return useraddress
    else: 
        if (add_user(username) == "error"):
            return "error"  
        else:
            return get_user_address(username)




#getUserGiftamount
#getUserGiftamount(username) get how much the user has donated to /u/bitcointip
def get_user_gift_amount(username):

    #if not user, add user
    add_user(username)

    sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='%s'" % (username)

    _mysqlcursor.execute(sql)
    results = _mysqlcursor.fetchall()
    for row in results:
        giftamount = row[5]
        return float(giftamount)

    #if nothing was returned, the user doesn't exist yet. Add them. and try again.
    if (add_user(username) == "error"):
        return "error"
    else:
        return get_user_gift_amount(username)



#hasUserRedeemedKarma
#checks to see if a user has gotten bitcoins from the reddit bitcoin faucet yet.
def has_user_redeemed_karma(username):

    #if not user, add user
    add_user(username)
    
    sql = "SELECT * FROM TEST_TABLE_FAUCET_PAYOUTS WHERE username='%s'" % (username)
    _mysqlcursor.execute(sql)
    results = _mysqlcursor.fetchall()
    for row in results:
        alreadyredeemed = True
        
    if (alreadyredeemed):
        print ("user has redeemed karma already.")
        return True
    else:
        print ("user has not redeemed karma yet.")
        return False


#doesTransactionExist
#double checks whether or not a transaction has already been done.
def does_transaction_exist(sender, receiver, timestamp):

    sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE sender_username='%s' AND receiver_username='%s' AND timestamp='%d'" % (sender, receiver, timestamp)
    _mysqlcursor.execute(sql)
    results = _mysqlcursor.fetchall()
    for row in results:
        #transaction already processed
        return True
    
    #transaction doesn't exist.
    return False

    
#create footer for the end of all PMs
def get_footer(username):
    footer = "\n\n---\n\n|||\n|:|:|\n| Account Owner: | **%s** |\n| Deposit Address: | **%s** |\n| Address Balance: | **%.8f BTC** *(~$%.2f USD)* \n|\n\n[About Bitcointip](http://www.reddit.com/r/bitcointip) (BETA!)" % (username, get_user_address(username), get_user_balance(username), round(get_user_balance(username)*_lastexchangeratefetched['USD'],2))
    return footer
    
    
    
#doTransaction
#do the transaction
def do_transaction(transaction_from, transaction_to, transaction_amount, tip_type, tip_id, tip_subreddit, tip_timestamp):

    #returns success message or failure reason
    
    print ("doing transaction")
    
    #Search for transaction in transaction list to prevent double processing!
    if (does_transaction_exist(transaction_from, transaction_to, tip_timestamp)):
        print ("Transaction does already exist.")
        return ("cancelled")

    #submit the transaction to the wallet.
    txid = bitcoind.transact(transaction_from, transaction_to, transaction_amount)
    
    print ("txid: ", txid)
    
    #based on the statusmessage, set the status and process.
    if (txid != "error"):
        status = "pending"
        
        if (bitcoind.validateaddress(transaction_to)['isvalid']):
            #we are sending to an address (not reversable)
            status = "completed"
    
        
        #do a transaction from sender to reciever for amount. put into TABLE_TRANSACTIONS
        sql = "INSERT INTO TEST_TABLE_TRANSACTIONS (transaction_id, sender_username, sender_address, receiver_username, receiver_address, amount_BTC, amount_USD, type, url, subreddit, timestamp, verify, statusmessage, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%.8f', '%.2f', '%s', '%s', '%s', '%f', '%s', '%s', '%s')" % (txid, transaction_from, transaction_from, transaction_to, transaction_to, transaction_amount, round(transaction_amount*_lastexchangeratefetched['USD'],2), tip_type, tip_id, tip_subreddit, tip_timestamp, "null", "null", status)
        _mysqlcursor.execute(sql)
        _mysqlcon.commit()
    
    
        #if tip is to bitcointip, add tip to giftamount for sender.
        if ( transaction_to.lower() == "bitcointip" ):
            oldgiftamount = get_user_giftamount(transaction_from)
            newgiftamount = oldgiftamount + transaction_amount
            sql = "UPDATE TEST_TABLE_USERS SET giftamount='%.8f' WHERE username='%s'" % (newgiftamount, transaction_from)
            _mysqlcursor.execute(sql)
            _mysqlcon.commit()
            
            bitcointipsubreddit = reddit.get_subreddit("bitcointip")
            #based on newgiftamount, set flair and make friend if applicable
            if (newgiftamount>=2):
                #bitcoin level
                reddit.get_redditor(transaction_from).friend()
                bitcointipsubreddit.set_flair(transaction_from, "Friend of Bitcointip", "bitcoin")
            elif (newgiftamount>=1):
                #gold level
                bitcointipsubreddit.set_flair(transaction_from, "Friend of Bitcointip", "gold")
            elif (newgiftamount>=0.5):
                #silver level
                bitcointipsubreddit.set_flair(transaction_from, "Friend of Bitcointip", "silver")
            elif (newgiftamount>=0.25):
                #bronze level
                bitcointipsubreddit.set_flair(transaction_from, "Friend of Bitcointip", "bronze")
                
            #make all transactions to 'bitcointip' completed
            sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE receiver_username='bitcointip'" 
            _mysqlcursor.execute(sql)
            _mysqlcon.commit()
        
        print ("Transaction Successful:", transaction_from, ">>>>", transaction_amount, ">>>>", transaction_to)
        
    else:
        #(txid == "error") the transaction didn't go through right. and is canceled
        
        status = "cancelled"
        
        #even though canceled, enter into transaction list but as cancelled
        sql = "INSERT INTO TEST_TABLE_TRANSACTIONS (transaction_id, sender_username, sender_address, receiver_username, receiver_address, amount_BTC, amount_USD, type, url, subreddit, timestamp, verify, statusmessage, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%.8f', '%.2f', '%s', '%s', '%s', '%f', '%s', '%s', '%s')" % (txid, transaction_from, transaction_from, transaction_to, transaction_to, transaction_amount, round(transaction_amount*_lastexchangeratefetched['USD'],2), tip_type, tip_id, tip_subreddit, tip_timestamp, "null", "null", status)
        _mysqlcursor.execute(sql)
        _mysqlcon.commit()
    print ("Transaction Cancelled:", transaction_from, ">>>>", transaction_amount, ">>>>", transaction_to)
    
    #cancelled or pending
    
    #update lastactive for the sender because they are using tips
    set_last_time("LASTACTIVE_"+transaction_from, round(time.time()))
    
    return status

    
    

#update_transactions
#updates pending transactions to completed or reversed depending on receiver activity
def update_transactions():
    print ("Updating Pending Transactions...")
    
    global _lastpendingupdatedtime
    global _lastpendingnotifiedtime
    
    ##get TRANSACTIONS_UPDATED timestamp from TEST_TABLE_RECENT
    _lastpendingupdatedtime = get_last_time("lastpendingupdatedtime")
    
    
    print ("Last Pending Transactions Update Time:", _lastpendingupdatedtime)
        
        
    ##do this once every day
    ##if (transactiontime + 21days)< receiverlastactive, process the reversal of the transaction to the senders new address, and set transactionstatus=reversed.

    if ((_lastpendingupdatedtime + (_intervalpendingupdate)) <= round(time.time())):
        ##if the transactions haven't been updated in 1 day, do the update.
        print ("Updating Pending Transactions")
    
        sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE status='pending'"
        _mysqlcursor.execute(sql)
        results = _mysqlcursor.fetchall()
        for row in results:
            transactionid = row[0]
            receiver = row[3]
            sender = row[1]
            timestamp = float(row[10])
            transactionamount = float(row[5])
            

            receiverlastactive = get_last_time("LASTACTIVE_"+receiver)
            if (receiverlastactive > timestamp):
                #mark transaction as completed because user has been active after transaction
                sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s" % (transactionid)
                _mysqlcursor.execute(sql)
                _mysqlcon.commit()
            elif ( round(time.time()) > (timestamp + _intervalpendingcancel) ):
                #transaction is older than 21 days and pending...try to reverse
                ##check to make sure the reciever has enough
                receiverbalance = get_user_balance(receiver)
                if (receiverbalance >= (transactionamount)):
                    ##the receiver has enough, just move the coins from the receiveraddress back to the new senderaddress
                    reversalamount = transactionamount - 0.0005
                    
                    reversalstatus = bitcoind.transact(receiver, sender, reversalamount)
                    
                    ##mark the transaction as reversed in the table
                    if(reversalstatus != "error"):
                        sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='reversed' WHERE transaction_id='%s'" % (transactionid)
                        _mysqlcursor.execute(sql)
                        _mysqlcon.commit()
                        print ("Transaction reversed: ", transactionid)
                    else:
                        ##the user doesn't have enough to reverse the transaction, they must have spent it in another way.
                        sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s'" % (transactionid)
                        _mysqlcursor.execute(sql)
                        _mysqlcon.commit()
                        print ("Transaction completed (user already spent funds):", transactionid)
                else:
                    ## the receiver doesn't have enough.  They must have already spent it
                    ##mark as completed instead of reversed.
                    sql = "UPDATE TEST_TABLE_TRANSACTIONS SET status='completed' WHERE transaction_id='%s'" % (transactionid)
                    _mysqlcursor.execute(sql)
                    _mysqlcon.commit()
                    print ("Transaction completed (user already spent funds):", transactionid)
            

        
        
        #Get ready to send out weekly notifications to users who have pending transactions to them that they need to accept.
        ##get TRANSACTIONS_NOTIFIED timestamp from TEST_TABLE_RECENT
            _lastpendingnotifiedtime = get_last_time("lastpendingnotifiedtime")
            print ("Last Notify Time:", _lastpendingnotifiedtime)
        
        
    
        
        ##do notifications weekly, not daily.
        if ((_lastpendingnotifiedtime + _intervalpendingnotify) <= round(time.time())):
            print ("Going through each user to see if need to notify")
    
            ##go through each user and compile list of pending transactions to them.
            sql = "SELECT * FROM TEST_TABLE_USERS WHERE 1"
            _mysqlcursor.execute(sql)
            result = _mysqlcursor.fetchall()
            for row in result:
                username = row[1]
                havependingtransaction = False
                
                sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE receiver_username='%s' AND status='pending' ORDER BY timestamp ASC" % (username)
                _mysqlcursor.execute(sql)
                resultb = _mysqlcursor.fetchall()
                for row in resultb:
                    havependingtransaction = True
                    oldesttransaction = float(row[10])
            
                if (havependingtransaction):
                
                    print (username, " has a pending transaction")
                    message = "One or more of your received tips is pending.  If you do not take action, your account will be charged and the tip will be returned to the sender.  To finalize your ownership of the tip, send a message to bitcointip with ACCEPT in the message body.  The oldest pending tip(s) will be returned to the sender in ~%d days." % (round((oldesttransaction + (_intervalpendingcancel) - round(time.time()))/(60*60*24)))
                    
                    ##Add on a list of transactions since $oldesttransaction
                    ##add first line of transaction table headers to the response.
                    transactionhistorymessage = "\n#**%s's Pending Transaction History***\n\nDate | Sender | Receiver | BTC | ~USD | Status |\n|:|:|:|:|:|:|\n" % (username)
                    k = 0

                    sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE (sender_username='%s' OR receiver_username='%s' ) AND timestamp>=%f ORDER BY timestamp DESC" % (username, username, oldesttransaction)
                    _mysqlcursor.execute(sql)
                    resultc = _mysqlcursor.fetchall()
                    for row in resultc:
                        if (k<10):
                            sender = row[1]
                            receiver_username = row[3]
                            receiver_address = row[4]
                            amount_BTC = float(row[5])
                            amount_USD = float(row[6])
                            status = row[13]
                            timestamp = float(row[10])
                            
                            ##if tip is sent directly to address with no username, display address.
                            if (receiver_username == ""):
                                receiver = receiver_address
                            else:
                                receiver = receiver_username
                                
                            date = time.strftime("%a %d-%b-%Y", time.gmtime())

                            ##add new transaction row to table being given to user
                            newrow = "| %s | %s | %s | %.8f | $%.2f | %s |\n" % (date, sender, receiver, amount_BTC, amount_USD, status)
                            transactionhistorymessage = transactionhistorymessage + newrow
                        else:
                            #k = 10
                            transactionhistorymessage = transactionhistorymessage + "**Transaction History Truncated.*\n\n"
                        k += 1
                    
                        
        
                    transactionhistorymessage = transactionhistorymessage + "**Only includes tips to or from your Reddit username.*\n\n"
        
                    message = message + transactionhistorymessage
                
                    #add footer
                    message = message + get_footer(username)
                
                    ##put message in to submit table
                    sql = "INSERT INTO TEST_TABLE_TOSUBMIT (type, replyto, subject, text, captchaid, captchasol, sent, timestamp) VALUES ('message', '%s', 'Bitcointip Pending Transaction(s) Notice', '%s', '', '', '0', '%f')" % (username, message, round(time.time()))
                    _mysqlcursor.execute(sql)
                    _mysqlcon.commit()
                
                    print ("Notification of Pending transaction(s) prepared for", username)
                    
                _lastpendingnotifiedtime = round(time.time())
            set_last_time("lastpendingnotifiedtime", _lastpendingnotifiedtime)
            print ("<br><br>TRANSACTIONS_INSERTED(NOTIFIED) to ", _lastpendingnotifiedtime)
                
            
        else:
        
            print ("Not time to make notifications yet.")
            
    
    
    
        _lastpendingupdatedtime = round(time.time())
        set_last_time("lastpendingupdatedtime", _lastpendingupdatedtime)
        print ("<br><br>TRANSACTIONS_UPDATED(UPDATED) to ", round(time.time()))
    
    else:
        print ("Not Updating Pending Transactions")
    

    
def eval_tip(thing):
    #evaluates a user tip, does the tip if valid, and then sends comment reply and messages if needed
    
    #See if the message author has a bitcointip account, if not, ignore them.  Must send PM to bot, or receive a tip to get an account.
    sql = "SELECT * FROM TEST_TABLE_USERS WHERE username='%s'" % (thing.author.name)
    _mysqlcursor.execute(sql)
    result = _mysqlcursor.fetchall()
    userhasaccount = False
    for row in result:
        userhasaccount = True

    #ignore user if they don't have an account.
    if (not userhasaccount):
        return False
    
    ##List the properties the tip could have
    transaction_from = thing.author.name
    tip_timestamp = thing.created_utc
    tip_id = thing.name
    
    if (thing.subreddit is not None):
        tip_subreddit = thing.subreddit.name.lower()
    else:
        tip_subreddit = "none"
        
    if (thing.dest=="bitcointip"):
        tip_type = "message"
    else:
        tip_type = "comment"
    
    #Now get the properties of the tip string
    ##isolate the tipping command
    regex_start_string = "(\+(bitcointip|bitcoin|tip|btctip|bittip|btc))" #start tip
    regex_bitcoinaddress_string = "(@?(1|3)[A-Za-z0-9]{25,35})" #bitcoin address
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
    
    #get transaction_to
    if (tip_command_redditusername):
        transaction_to = tip_command_redditusername.strip('@')
    elif (tip_command_bitcoinaddress):
        transaction_to = tip_command_bitcoinaddress
    elif (tip_type == "comment"):
        #recipient not specified, get author of parent comment
        linkid = comment.link_id[3:]
        parentpermalink = somecomment.permalink.replace(comment.name[3:], comment.parent_id[3:])
        print ("parentpermalink", parentpermalink)
        if (linkid==new):
            parentcomment = reddit.get_submission(parentpermalink)
        else:
            parentcomment = reddit.get_submission(parentpermalink).comments[0]
        transaction_to = parentcomment.author.name
    elif (tip_type == "message"):
        #malformed tip
        #must include recipient
        #error
        cancelmessage = "You must specify a recipient username or bitcoinaddress."
        
    
    #get transaction_amount
    if (tip_command_bitcoinamount):
        transaction_amount = float(tip_command_bitcoinamount.strip('B &bitcoin; btc BTC'))
    elif (tip_command_fiatamount):
        transaction_amount = round((float(tip_command_fiatamount.strip('$ usd USD'))/_lastexchangeratefetched['USD']),8)
    elif (tip_command_all):
            senderbalance = get_user_balance(transaction_from)
            transaction_amount = (senderbalance - 0.0005)
            transaction_amount = round(amount, 8)
    elif (tip_command_flip):
        if (get_user_balance(transaction_from)>=0.0105):
            if (get_user_gift_amount(transaction_from)>=0.25):
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
    elif (tip_command_internet):
        if (get_user_gift_amount(transaction_from)>=1):
            if (tip_command_internet.find('s')):
                transaction_amount = 0.02
                if (get_user_balance(transaction_from)<0.0205):
                    cancelmessage = "You don't have 2 internets to give"
            else:
                if (get_user_balance(transaction_from)>=0.0105):
                    transaction_amount = 0.01
                else:
                    cancelmessage = "You don't have an internet to give"
        else:
            #error: not donated enough
            cancelmessage = "You have not donated enough to use the '+1 internet' command."
        
        
    ##check conditions to cancel the transaction and return error message
    if (transaction_amount<=0 and (not tip_command_flip) and cancelmessage==""):
        cancelmessage = "You cannot send an amount <= 0. That is just silly."
    elif (transaction_amount+0.0005 > get_user_balance(transaction_from) and cancelmessage==""):
        cancelmessage = "You do not have enough in your account.  You have %.8f BTC, but need %.8f BTC (do not forget about the 0.0005 BTC fee per transaction)." % (get_user_balance(transaction_from), transaction_amount+0.0005)
    elif ( tip_type=="comment" and (tip_subreddit not in allowedsubreddits) and (get_user_gift_amount(transaction_from)<2) and cancelmessage==""):
        cancelmessage = "The %s subreddit is not currently supported for you." % (tip_subreddit)
    elif ((transaction_from in bannedusers) and transaction_from!="" and cancelmessage==""):
        cancelmessage="You are not allowed to send or receive money."
    elif ((transaction_to in bannedusers) and transaction_to!="" and cancelmessage==""):
        cancelmessage="The user %s is not allowed to send or receive money." % (transaction_to)
    elif (transaction_to == transaction_from and cancelmessage==""):
        cancelmessage="You cannot send any amount to yourself, that is just silly."
    elif (transaction_to == "" and cancelmessage==""):
        cancelmessage="You must specify a recipient username or bitcoin address."

    if (not cancelmessage):
        transaction_status = doTransaction(transaction_from, transaction_to, transaction_amount, tip_type, tip_id, tip_subreddit, tip_timestamp)
    
    #based on the variables, form messages.
    verifiedmessage = "[*%s &nbsp; >>>> &nbsp; %.8f BTC (~$%.2f) &nbsp; >>>> &nbsp; %s*](http://reddit.com/r/bitcointip)" % (transaction_from, transaction_amount, round(transaction_amount*_lastexchangeratefetched['USD'], 2), transaction_to)
    
    rejectedmessage = "[~~*%s &nbsp; >>>> &nbsp; %.8f BTC (~$%.2f) &nbsp; >>>> &nbsp; %s*~~](http://reddit.com/r/bitcointip)" % (transaction_from, transaction_amount, round(transaction_amount*_lastexchangeratefetched['USD'], 2), transaction_to)
    
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
    if (tip_type == "comment" and tip_command_verify.lower()!="noverify" and ((tip_subreddit in allowedsubreddits) or (get_user_gift_amount(transaction_from)>=2))):
        #Reply to the comment
        if (transaction_status=="completed" or transaction_status=="pending"):
            commentreplymessage = flipmessage
            if (flipresult==1 or  (not tip_command_flip)):
                commentreplymessage += verifiedmessage
        else:
            commentreplymessage += rejectedmessage
        
    if (commentreplymessage):
        #if comment reply is prepared, send it
        #enter reply into table
        sql = "INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp)  VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%f')" % ("", tip_type, comment.permalink, "", commentreplymessage, "", "", "0", tip_timestamp)
        _mysqlcursor.execute(sql)
        _mysqlcon.commit()
        
    
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
        pmsendermessage += get_footer(transaction_from)
    
    if (pmsendermessage):
        #if pm to sender is prepared, send it
        #enter message into table
        sql = "INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp)  VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%f')" % ("", tip_type, transaction_from, pmsendersubject, pmsendermessage, "", "", "0", tip_timestamp)
        _mysqlcursor.execute(sql)
        _mysqlcon.commit()
    
    #Send a message to the receiver under what conditions?
    #only PM receiver if tip_type is a message and success
    if (tip_type == "message" and transaction_status == "pending"):
        #PM the Receiver
        pmreceiversubject = "Successful Bitcointip Notice"
        pmreceivermessage = flipmessage +verifiedmessage 
        
        #add footer to PM
        pmreceivermessage += get_footer(transaction_to)
        
    if (pmreceivermessage):
        #if pm to receiver is prepared, send it
        #enter message into table
        sql = "INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp)  VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%f')" % ("", tip_type, transaction_to, pmreceiversubject, pmreceivermessage, "", "", "0", tip_timestamp)
        _mysqlcursor.execute(sql)
        _mysqlcon.commit()
            
    if (tip_command):
        #tip found and done
        return True
    else:
        #no tip in this text
        return False

    
#find_message_command
#returns text result as message to send back.
def find_message_command(message): #array
    
    
    if (_botstatus == "down"):
        #if down, just reply with a down message to all messages
        returnstring = "The bitcointip bot is currently down.\n\n[Click here for more information about the bot.](http://www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/)\n\n[Click here for more information about bitcoin.](http://www.weusecoins.com/)\n\n[Click here to get a bitcoin wallet.](https://blockchain.info/wallet/)"
    
    #See if the message author has a bitcointip account, if not, make one for them.
    add_user(message.author.name)
    
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
        faucetbalance = get_user_balance("bitcointipfaucetdepositaddress")
        
        if (not has_user_redeemed_karma(message.author.name)):
            #if not redeemed yet, check for a valid bitcoin address

            print ("user has not redeemed karma yet.")

            if (bitcoind.validateaddress(karmabitcoinaddress)['isvalid']):
            
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
                if ( (linkkarma>minlinkkarma) and (commentkarma>mincommentkarma) and (totalkarma>mintotalkarma)):
                    #User has enough karma
                    print ("user has enough karma")
                    
                    if ( karmabitcoinamount < 0.002 ):
                        bitcoinamount = karmabitcoinamount + defaultbitcoinamount
                        print ("give user defualt amount too.")
                    else:
                        bitcoinamount = karmabitcoinamount
                        print ("don't give user default amount.")
                    
                    #check to make sure the faucet has enough.
                    if ( faucetbalance > (bitcoinamount + 0.0005) ):
                        
                        #The reddit bitcoin faucet has enough
                        print ("the reddit bitcoin faucet has: %.8f BTC", faucetbalance)

                        #go ahead and send the bitcoins to the user
                        txid = bitcoind.transact("bitcointipfaucetdepositaddress", karmabitcoinaddress, bitcoinamount)

                        if (txid != "error"):
                            print ("no error, transaction done, bitcoins en route to %s." % (karmabitcoinaddress) )
                            #reply to their message with success
                            returnstring = "Your bitcoins are on their way.  Check the status here: http://blockchain.info/address/%s\n\nIf you do not want your bitcoins, consider passing them on to a [good cause](https://en.bitcoin.it/wiki/Donation-accepting_organizations_and_projects)." % (karmabitcoinaddress)
                            
                            #insert the transaction to the list of TABLE_FAUCET_PAYOUTS
                            sql = "INSERT INTO TEST_TABLE_FAUCET_PAYOUTS (transaction_id, username, address, amount, timestamp) VALUES ('%s', '%s', '%s', '%.8f', '%f')" % (txid, message.author.name, karmabitcoinaddress, bitcoinamount, round(time.time()))
                            _mysqlcursor.execute(sql)
                            _mysqlcon.commit()

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
                    print ("%s doesn't have enough karma." % message.author.name)
                    returnstring = "You do not have enough karma to get bitcoins. You need at least %f Comment Karma to be eligible (You only have %f). Keep redditing or try this bitcoin faucet: https://freebitcoins.appspot.com" % (mincommentkarma, commentkarma)

            else:
                #no valid bitcoin address detected
                print ("No valid bitcon address detected.")
                returnstring = "No valid bitcoin address detected.  Send the string \"REDEEM KARMA: 1YourBitcoinAddressHere\" but put in YOUR bitcoin address."

        else:
            print ("%s has already redeemed karma" % (message.author.name))
            #user has already redeemed karma, can't do it again.
            returnstring = "You have already 'sold' your karma for bitcoins.  You can only do this once."
    
    
    #"TRANSACTIONS"/"HISTORY"/"ACTIVITY"
    #Gives use a list of their transactions including deposits/withdrawals/sent/recieved
    regex_history = re.compile("((TRANSACTIONS)|(HISTORY)|(ACTIVITY))",re.IGNORECASE)
    command_history = regex_history.search(message.body)
    
    if (command_history and returnstring==""):
        
        #add first line of transaction table headers to the response.
        transactionhistorymessage = "\n#**%s Transaction History***\n\nDate | Sender | Receiver | BTC | ~USD | Status |\n|:|:|:|:|:|:|\n" % (message.author.name)
        k = 0

        sql = "SELECT * FROM TEST_TABLE_TRANSACTIONS WHERE sender_username='%s' OR receiver_username='%s' ORDER BY timestamp DESC" % (message.author.name, message.author.name)
        _mysqlcursor.execute(sql)
        result = _mysqlcursor.fetchall()
        for row in result:
            if (k<11):
                sender = row[1]
                receiver_username = row[3]
                receiver_address = row[4]
                amount_BTC = float(row[5])
                amount_USD = float(row[6])
                status = row[13]
                timestamp = float(row[10])
                
                ##if tip is sent directly to address with no username, display address.
                if (receiver_username == ""):
                    receiver = receiver_address
                else:
                    receiver = receiver_username
                
                date = time.strftime("%a %d-%b-%Y", time.gmtime())
                
                
                if (sender == message.author.name):
                    senderbold = "**"
                    amountsign = "*"
                elif (receiver == message.author.name):
                    receiverbold = "**"
                    amountsign = "**"
                    
                ##add new transaction row to table being given to user
                newrow = "| %s | %s%s%s | %s%s%s | %s%.8f%s | %s$%.2f%s | %s |\n" % (date, senderbold, sender, senderbold, receiverbold, receiver, receiverbold, amountsign, amount_BTC, amountsign, amountsign, amount_USD, amountsign, status)
                transactionhistorymessage = transactionhistorymessage + newrow

            elif (k == 11):
                ##if there are more than 30 transactions, tell them there are some left out after the table.
                transactionhistorymessage = transactionhistorymessage + "**Transaction History Truncated.*\n\n"
                break
            k+=1

            ##end
        
        #if no transactions, say so
        if (k == 0):
            transactionhistorymessage += "\n\n**You have no transactions.**\n\n"

        
        transactionhistorymessage += "\n**Only includes tips to or from your Reddit username.*\n\n\n"
        
        returnstring += transactionhistorymessage

    #Let user import a private key to use
    ###"REPLACE PRIVATE KEY WITH: $privatekey
    ###TRANSFER BALANCE: Y/N"
    regex_importkey = re.compile("((REPLACE PRIVATE KEY WITH:)( )?(5[a-zA-Z0-9]{35,60})(( )*(\n)*( )*)(TRANSFER BALANCE:)( )?(Y|N))",re.IGNORECASE)
    command_importkey = regex_importkey.search(message.body)
    
    if (command_importkey and returnstring==""):

        if (get_user_gift_amount(message.author.name) >= 0.5):
        #do it
        
            print ("<br>Private Key detected...")
            privatekey = command_importkey.groups(3)
            transfer = command_importkey.groups(10)
            
            print ("Private Key: XXXXX")
            print ("Transfer: ", transfer)
            
            authoroldaddress = get_user_address(message.author.name)
            authoroldbalance = get_user_balance(message.author.name)
            
            print ("authoroldaddress: ", authoroldaddress)
            print ("authoroldbalance: ", authoroldbalance)
            
            
            
            
            importstatus = (bitcoind.importprivkey(privatekey, "thisisatemporarylabelthatnobodyshoulduse"))
            
            print ("importstatus: ", importstatus)
            
            if (importstatus):
            
                authornewaddress = bitcoind.getaddressesbyaccount("thisisatemporarylabelthatnobodyshoulduse")[0]
                authornewbalance = bitcoind.getbalance("thisisatemporarylabelthatnobodyshoulduse")
                
                print ("authornewaddress: ", authornewaddress)
                print ("authornewbalance: ", authornewbalance)
            
                setaccountold = bitcoind.setaccount(authoroldaddress, "OLD ADDRESS: "+message.author.name)
                setaccountnew = bitcoind.setaccount(authornewaddress, message.author.name)
                
                print ("setaccountold: ", setaccountold)
                print ("setaccountnew: ", setaccountnew)
                
                if (setaccountold and setaccountnew):
                
                    returnstring = "Replacement successful. Your new bitcoin address is: %s.\n\nYour old bitcoin address was: ~~%s~~." % (authornewaddress, authoroldaddress)
                if (transfer.lower() == "y" and authoroldbalance != 0):
                    moveamount = authoroldbalance - 0.0005
                    movedstatus = bitcoind.transact(authoroldaddress, authornewaddress, moveamount) 
                    print ("movedstatus: ", movedstatus)
                    if (movedstatus != "error"):
                        returnstring += "\n\nYour old balance of %.8f is being moved to your new address." % (moveamount)
                        authornewbalance += moveamount
                    else:
                        returnstring += "\n\nThere was a problem moving your funds. Either you have too little or something went wrong. Please report if there is a problem."
            
                ##update user table entry with new balance and new address

                sql = "UPDATE TEST_TABLE_USERS SET address='%s' WHERE username='%s'" % (authornewaddress, message.author.name)
                _mysqlcursor.execute(sql)
                _mysqlcon.commit()
                
            else:
                returnstring = "There was a problem setting up your new account. Please report if there is a problem."
        
        else:
            returnstring = "There was a problem importing the private key.  Make sure it is in the correct format for bitcoind import."

    else:
        ##not enough gift.
        returnstring = "You have not donated enough to use that command."   
    
    ##ACCEPT PENDING TRANSACTIONS
    ##"ACCEPT"
    regex_accept = re.compile("(ACCEPT)",re.IGNORECASE)
    command_accept = regex_accept.search(message.body)
    
    if (command_accept and returnstring==""):
        set_last_time("LASTACTIVE_"+message.author.name, round(time.time()))
        returnstring = "All pending transactions will be accepted.  No currently existing tips to you will be reversed."
    

    
    ##CHECK FOR MESSAGE TIP (take care of sending all messages here, return empty string, telling eval_messages to not send any more messages.
    
    if (eval_tip(message)):
        #if returns 1, then a tip was found.
        #only do one command per message, so stop looking for more commands
        #messages sent in eval_tip.
        return ""
        
        
        
    ##HELP
    regex_help = re.compile("(HELP)",re.IGNORECASE)
    command_help = regex_help.search(message.body)
    
    if (command_help and returnstring==""):
        returnstring = "Check the [Help Page](http://www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/)."
        
        
    ##NO COMMAND FOUND DO YOU NEED HELP?
    if (returnstring == ""):    
        returnstring = "This is the bitcointip bot.  No command was found in your message.\n\nTo fund your account, send bitcoins to your Deposit Address.\n\nFor help with commands, see [This Page](http://www.reddit.com/r/test/comments/11iby2/bitcointip_tip_redditors_with_bitcoin/).\n\n*Replies from the bot take on average 7.5 minutes but may take 30 minutes or more in some cases.*\n\n*Deposits are updated once per hour.*"
        
        

    ##ALL MESSAGES ADD FOOTER TO END OF ANY MESSAGE
        
    returnstring += get_footer(message.author.name)

        
    ##return returnstring;
    returnsubject = "Re: " + message.subject
    #insert returnstring into TEST_TABLE_TOSUBMIT
    #enter message into table
    sql = "INSERT INTO TEST_TABLE_TOSUBMIT (tosubmit_id, type, replyto, subject, text, captchaid, captchasol, sent, timestamp)  VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%f')" % ("", "message", message.author.name, returnsubject, returnstring, "", "", "0", message.created_utc)
    _mysqlcursor.execute(sql)
    _mysqlcon.commit()
    
    



#eval_messages
#get new messages and go through each one looking for a command, then respond.
def eval_messages():
    print ("Checking Messages...")
    
    global _lastmessageevaluated
    global _lastmessageevaluatedtime
    
    #get some unread messages.
    newest_message_evaluated_time = 0
    
    unread_messages = _reddit.user.get_unread(limit=1)
    for message in unread_messages:
        if (not message.was_comment):
            #ignore self messages and bannedusers messages/comments
            if ((message.author.name != "bitcointip") and (message.author.name not in _bannedusers)): 
                print ("Found new message from: %s, (%s)" % (message.author.name, message.subject))
                #check message for command and reply
                find_message_command(message)
                #mark as read
                message.mark_as_read()
                if (message.created_utc>newest_message_evaluated_time):
                    newest_message_evaluated_time = message.created_utc
            else:
                print ("IGNORE MESSAGE (outgoing)")
        else:
            print ("IGNORE MESSAGE (comment reply)")
            
    if (newest_message_evaluated_time):
        _lastmessageevaluated = newest_message_evaluated_time
        set_last_time("lastmessageevaluated", _lastmessageevaluated)
        
    _lastmessageevaluatedtime = round(time.time())
    set_last_time("lastmessageevaluatedtime",_lastmessageevaluatedtime)
    

#find_comment_command
#find a command in a user comment
def find_comment_command(comment):
    eval_tip(comment)




#eval_comments
# get new comments and go through each one looking for a command, then respond.
def eval_comments():
    print ("Checking Comments...")
    
    global _lastcommentevaluatedtime
    global _lastcommentevaluated
    global _lastfriendcommentevaluatedtime
    global _lastfriendcommentevaluated
    
    multiredditstring = ""
    for x in allowedsubreddits:
        multiredditstring += x + "+"
    
    multi_reddits = _reddit.get_subreddit(multiredditstring)
    
    #go through comments of allowed subreddits but NOT friendsofbitcointip
    _lastcommentevaluatedtime = get_last_time("lastcommentevaluatedtime")
    
    first_comment_this_loop = None
    print ("checking comments")
    multi_reddits_comments = multi_reddits.get_comments(limit=1)
    for comment in multi_reddits_comments:
        if (not first_comment_this_loop):
            first_comment_this_loop = comment.created_utc
        if (comment.created_utc <= _lastcommentevaluated):
            print ("old comment reached")
            break
        else:
            if ((comment.author.name not in _friendsofbitcointip) and (comment.author.name not in _bannedusers)):#exclude friendsofbitcointip and banned users
                #print ("(",comment.subreddit,")",comment.author,":",comment.body)
                find_comment_command(comment)
    _lastcommentevaluated = first_comment_this_loop
    _lastcommentevaluatedtime = round(time.time())
    #write updated lastcommentevaluatedtimestamp to table.
    set_last_time("lastcommentevaluated", _lastcommentevaluated)
    set_last_time("lastcommentevaluatedtime", _lastcommentevaluatedtime)
    
     
    #now go through friendsofbitcointip separately
    
    _lastfriendcommentevaluatedtime = get_last_time("lastfriendcommentevaluatedtime")
    friends_reddit = _reddit.get_subreddit("friends")
    
    first_comment_this_loop = None
    print ("checking friend comments")
    friends_reddit_comments = friends_reddit.get_comments(limit=1)
    for comment in friends_reddit_comments:
        if (not first_comment_this_loop):
            first_comment_this_loop = comment.created_utc
        if (comment.created_utc <= _lastfriendcommentevaluated):
            print ("old friend comment reached")
            break
        else:
            #print ("(",comment.subreddit,")",comment.author,":",comment.body)
            find_comment_command(comment)
    _lastfriendcommentevaluated = first_comment_this_loop.created_utc
    #write updated lastfriendcommentevaluatedtimestamp to table.
    _lastfriendcommentevaluatedtime = round(time.time())
    set_last_time("_lastfriendcommentevaluatedtime", _lastfriendcommentevaluatedtime)
    set_last_time("_lastfriendcommentevaluated", _lastfriendcommentevaluated)


#submit_messages
#submits outgoing messages/comments to reddit.com
def submit_messages():
    print ("Submitting Messages and comment replies...")
    
    #go through each entry, and try to submit reply.
    #if reply is sent out, mark message as sent=1.
    #if reply is not sent because of error, mark as sent=x.

    going = True
    
    ##go through list of tosubmit orderby timestamp from oldest to newest
    sql = "SELECT * FROM TEST_TABLE_TOSUBMIT WHERE sent='0' ORDER BY timestamp ASC"
    _mysqlcursor.execute(sql)
    result = _mysqlcursor.fetchall()
    for row in result:
        if (going):
            print ("Trying to go through each unsent message/comment")
            type = row[1]
            replyto = row[2] #user if type=message, permalink if type=comment
            subject = row[3]
            text = row[4]
            captchaid = row[5]
            captchasol = row[6]
            sent = float(row[7])
            timestamp = float(row[8])
            
            print ("Type:", type)
            
            if ( type == "comment" ): 
                comment = _reddit.get_submission(replyto).comments[0]
                
                try:
                    comment.reply(text)
                    print ("Comment Sent")
                    ##it worked.
                    sql = "UPDATE TEST_TABLE_TOSUBMIT SET sent=1 WHERE type='%s' AND timestamp='%f' AND replyto='%s'" % (type, timestamp, replyto)
                    _mysqlcursor.execute(sql)
                    _mysqlcon.commit()
                    print ("Comment Marked as delivered")
                    
                except Exception as e:
                    print ("Error:",e)
                    print ("Comment not delivered...skipping for now.")
                

            if ( type == "message" ): 
                
                #try to send a personal message
                try:
                    _reddit.send_message(replyto,subject,message)
                    print ("message sent")
                    sql = "UPDATE TEST_TABLE_TOSUBMIT SET sent=1 WHERE type='%s' AND timestamp='%f' AND replyto='%s'" % (type, timestamp, replyto)
                    _mysqlcursor.execute(sql)
                    _mysqlcon.commit()
                    print ("Message marked as delivered")
                        
                except Exception as e:
                    print ("message not sent", e)
                    if (e == "Error `that user doesn't exist` on field `to`"):
                        #user doesn't exist, cancel the message
                        sql = "UPDATE TEST_TABLE_TOSUBMIT SET sent=x WHERE type='%s' AND timestamp='%f' AND replyto='%s'" % (type, timestamp, replyto)
                        _mysqlcursor.execute(sql)
                        _mysqlcon.commit()
                        print ("user doesn't exist. message cancelled.")

                
                    







######################################################################
#MAIN
######################################################################
#DETAILS:
_MYSQLhost = "???"
_MYSQLlogin = "???"
_MYSQLpass = "???"
_MYSQLdbname = "???"
_MYSQLport = 0

_BITCOINDlogin = "???"
_BITCOINDpass = "???"
_BITCOINDip = "???"
_BITCOINDport = "????"
_BITCOINDsecondpass = "???"

_REDDITbotusername = "???"
_REDDITbotpassword = "???"
_REDDITuseragent = "???"

# BOTSTATUS (DOWN/UP)
_botstatus = "down"


#update exchange rate from the charts every 3 hours
_intervalupdateexchangerate = 60*60*3
#update transactions (pending->completed or pending->cancelled) every 24 hours
_intervalpendingupdate = 60*60*24*1
#update transactions (pending->cancelled) when transactions are 21 days old
_intervalpendingcancel = 60*60*24*21
#notify users that they have a pending transaction for them every 7 days.
_intervalpendingnotify = 60*60*24*7


# CONNECT TO MYSQL DATABASE
_mysqlcon = pymysql.connect(host=_MYSQLhost, port=_MYSQLport, user=_MYSQLlogin, passwd=_MYSQLpass, db=_MYSQLdbname)
_mysqlcursor = _mysqlcon.cursor()
print ("Connected to MYSQL.")

# CONNECT TO BITCOIND SERVER
_jsonRPCClientString = "http://"+_BITCOINDlogin+":"+_BITCOINDpass+"@"+_BITCOINDip+":"+_BITCOINDport+"/"
bitcoind.access = ServiceProxy(_jsonRPCClientString)
print("Connected to BITCOIND.")

# CONNECT TO REDDIT.COM
_reddit = praw.Reddit(user_agent = _REDDITuseragent)
_reddit.login(_REDDITbotusername, _REDDITbotpassword)
print("Connected to REDDIT.")


#TIMINGS

#LAST TIME THIS WAS DONE (Make default to right now to avoide double evaluations)
_lastcommentevaluatedtime = round(time.time())
_lastfriendcommentevaluatedtime = round(time.time())
_lastmessageevaluatedtime = round(time.time())
_lastallowedsubredditsfetchedtime = round(time.time())
_lastfriendsofbitcointipfetchedtime = round(time.time())
_lastbannedusersfetchedtime = round(time.time())
_lastexchangeratefetchedtime = round(time.time())
_lastpendingupdatedtime = round(time.time())
_lastpendingnotifiedtime = round(time.time())

_lastcommentevaluatedtime = get_last_time("lastcommentevaluatedtime")
_lastfriendcommentevaluatedtime = get_last_time("lastfriendcommentevaluatedtime")
_lastmessageevaluatedtime = get_last_time("lastmessageevaluatedtime")
_lastallowedsubredditsfetchedtime = get_last_time("lastallowedsubredditsfetchedtime")
_lastfriendsofbitcointipfetchedtime = get_last_time("lastfriendsofbitcointipfetchedtime")
_lastbannedusersfetchedtime = get_last_time("lastbannedusersfetchedtime")
_lastexchangeratefetchedtime = get_last_time("lastexchangeratefetchedtime")
_lastpendingupdatedtime = get_last_time("lastpendingupdatedtime")
_lastpendingnotifiedtime = get_last_time("lastpendingnotifiedtime")

_lastcommentevaluated = get_last_time("lastcommentevaluated")
_lastfriendcommentevaluated = get_last_time("lastfriendcommentevaluated")
_lastmessageevaluated = get_last_time("lastmessageevaluated")
_lastallowedsubredditsfetched = get_last_time("lastallowedsubredditsfetched")
_lastfriendsofbitcointipfetched = get_last_time("lastfriendsofbitcointipfetched")
_lastbannedusersfetched = get_last_time("lastbannedusersfetched")
_lastexchangeratefetched = get_last_time("lastexchangeratefetched")
_lastpendingupdated = get_last_time("lastpendingupdated")
_lastpendingnotified = get_last_time("lastpendingnotified")


#get list of allowed subreddits by checking bitcointip's reddits/mine
_allowedsubreddits = []
refresh_allowed_subreddits()

#get list of friends from reddit
_friendsofbitcointip = []
refresh_friends()

#get list of banned users from reddit
_bannedusers = []
refresh_banned_users()

#Initialize Exchange rates
_lastexchangeratefetched = { 'USD':0, 'AUD':0, 'CAD':0, 'EUR':0, 'JPY':0, 'GBP':0}

refresh_exchange_rate()




_looping = 1
# WHILE THE BOT DOESN'T HAVE ANY PROBLEMS, KEEP LOOPING OVER EVALUATING COMMENTS, MESSAGES, AND SUBMITTING REPLIES
while(_looping):

if (True):

    start_loop_time = round(time.time())

    #UNLOCK BITCOIND WALLET
    print ("Unlocking Bitcoin Wallet...")
    print  (bitcoind.walletpassphrase(_BITCOINDsecondpass, 6000))

    #CHECK/UPDATE EXCHANGE RATE
    refresh_exchange_rate()

    #CHECK FOR NEW REDDIT PERSONAL MESSAGES
    eval_messages()

    #CHECK FOR NEW COMMENTS
    if (_botstatus == "up"): #if down, don't check comments
        eval_comments()

    #UPDATE PENDING TRANSACTIONS
    if (_botstatus == "up"): #if down, don't update pending transactions
        update_transactions()
    
    #SUBMIT MESSAGES IN OUTBOX TO REDDIT
        submit_messages()

    #LOCK BITCOIND WALLET
        print ("Locking Bitcoin Wallet")
        print (bitcoind.walletlock())
        
    #todo: sleep for a bit if all that didn't take very long.
    time.sleep(300)

#LOCK BITCOIND WALLET AT PROGRAM END
print ("Locking Bitcoin Wallet")
print (bitcoind.walletlock())

