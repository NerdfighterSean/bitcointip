from functools import wraps

def my_decorator(f):
	@wraps(f)
	def wrapper(*args, **kwds):
		try:
			return f(*args, **kwds)
		except Exception as e:
			print ("Error: %s" % e.error['message'])
			return "error"
	return wrapper
	
'''
addmultisigaddress
<nrequired> <'["key","key"]'> [account]
Add a nrequired-to-sign multisignature address to the wallet. Each key is a bitcoin address or hex-encoded public key. If [account] is specified, assign address to [account].	 
N
Returns:
'''
@my_decorator
def addmultisigaddress(nrequired, keys, account="DEFAULT ACCOUNT"):
		return access.addmultisigaddress(nrequired, keys, account)

'''
backupwallet
<destination>
Safely copies wallet.dat to destination, which can be a directory or a path with filename.	 
N
Returns:
"None"
'''
@my_decorator
def backupwallet(destination):
		return access.backupwallet(destination)

'''
createrawtransaction
[{"txid":txid,"vout":n},...] {address:amount,...}	
version 0.7 Creates a raw transaction spending given inputs.	 
N
Returns:
'''
@my_decorator
def createrawtransaction(txidvout, addressamount):
		return access.createrawtransaction(txidvout, addressamount)
		
'''
decoderawtransaction
<hex string>
version 0.7 Produces a human-readable JSON object for a raw transaction.	 
N
Returns:
'''
@my_decorator
def decoderawtransaction(hexstring):
		return access.decoderawtransaction(hexstring)

'''
dumpprivkey
<bitcoinaddress>
Reveals the private key corresponding to <bitcoinaddress>	 
Y
Returns:
L4Qbhp6g9KgcMfZbFZifqpoAmW5p59kGsm5MMFe8jdrpS4CW3TwH
'''
@my_decorator
def dumpprivkey(bitcoinaddress):
		return access.dumpprivkey(bitcoinaddress)

'''
encryptwallet
<passphrase>
Encrypts the wallet with <passphrase>.	 
N
Returns:
wallet encrypted; Bitcoin server stopping, restart to run with encrypted wallet.  The keypool has been flushed, you need to make a new backup.
'''
@my_decorator
def encryptwallet(passphrase):
		return access.encryptwallet(passphrase)

'''
getaccount
<bitcoinaddress>
Returns the account associated with the given address.	 
N
Returns:
Billybob
'''
@my_decorator
def getaccount(bitcoinaddress):
		return access.getaccount(bitcoinaddress)

'''
getaccountaddress
<account>
Returns the current bitcoin address for receiving payments to this account.	 
N
Returns:
15gDL1qBugojebw2KWrwjk4qkuz9npTB4X
'''
@my_decorator
def getaccountaddress(account):
		return access.getaccountaddress(account)

'''
getaddressesbyaccount
<account>
Returns the list of addresses for the given account.	 
N
Returns:
['19b1sQojd9t5PHYdArS7hFUV7vzshNGxuk', '14DDpewYAVTSKmPDLXkUs38L794eqGMuvc', '16Dm5XHzxvmea2oTrMK6wbeWg1vXjcSucd', '1LPr67nfnouTsfZYCbQ8kkTkgCimdK41Po', '19rHqHREBfXtGzfHFCXbAJhmhrJY1e2pT1', '19ouPe7SyfrjKwV6mBmFQUr7WrhP9Ab4CW', '17cE6gYZeqiHPC9fLEoR7pQckw5N3WKz2c', '1Km5mXNR7Gj87E9fyp3u6EJU9TZTzqa6PZ', '15gDL1qBugojebw2KWrwjk4qkuz9npTB4X', '1HzQowH3tdkTf9HUQ1yGoMeNhVRG2GKYJM']
'''
@my_decorator
def getaddressesbyaccount(account):
		return access.getaddressesbyaccount(account)

'''
getbalance
[account] [minconf=1]
If [account] is not specified, returns the server's total available balance.
If [account] is specified, returns the balance in the account.	 
N
Returns:
0E-8
'''
@my_decorator
def getbalance(account, minconf=0):
		return access.getbalance(account, minconf)

'''
getblock
<hash>
Returns information about the given block hash.	 
N
Returns:
'''
@my_decorator
def getblock(hash):
		return access.getblock(hash)

'''
getblockcount
Returns the number of blocks in the longest block chain.	 
N
Returns:
205775
'''
@my_decorator
def getblockcount():
		return access.getblockcount()

'''
getblockhash
<index>
Returns hash of block in best-block-chain at <index>	 
N
Returns:
'''
@my_decorator
def getblockhash(index):
		return access.getblockhash(index)

'''
getconnectioncount
Returns the number of connections to other nodes.	 
N
Returns:
41
'''
@my_decorator
def getconnectioncount():
		return access.getconnectioncount()

'''
getdifficulty
Returns the proof-of-work difficulty as a multiple of the minimum difficulty.	 
N
Returns:
3304356.39299034
'''
@my_decorator
def getdifficulty():
		return access.getdifficulty()

'''
getgenerate
Returns true or false whether bitcoind is currently generating hashes	 
N
Returns:
False
'''
@my_decorator
def getgenerate():
		return access.getgenerate()

'''
gethashespersec
Returns a recent hashes per second performance measurement while generating.	 
N
Returns:
0
'''
@my_decorator
def gethashespersec():
		return access.gethashespersec()

'''
getinfo
Returns an object containing various state info.	 
N
Returns:
{'balance': Decimal('0E-8'), 'keypoolsize': 101, 'unlocked_until': 1351649589, 'testnet': False, 'version': 79900, 'walletversion': 60000, 'difficulty': Decimal('3304356.39299034'), 'protocolversion': 60002, 'connections': 12, 'proxy': '', 'errors': '', 'paytxfee': Decimal('0E-8'), 'keypoololdest': 1351642673, 'blocks': 205776}
'''
@my_decorator
def getinfo():
		return access.getinfo()

'''
getmemorypool
[data]
If [data] is not specified, returns data needed to construct a block to work on:
"version" : block version
"previousblockhash" : hash of current highest block
"transactions" : contents of non-coinbase transactions that should be included in the next block
"coinbasevalue" : maximum allowable input to coinbase transaction, including the generation award and transaction fees
"time" : timestamp appropriate for next block
"bits" : compressed target of next block
If [data] is specified, tries to solve the block and returns true if it was successful.
N
Returns:
'''
@my_decorator
def getmemorypool(data=""):
		return access.getmemorypool(data)

'''
getmininginfo
Returns an object containing mining-related information:
N
Returns:
{'difficulty': Decimal('3304356.39299034'), 'generate': False, 'genproclimit': -1, 'pooledtx': 1127, 'blocks': 205775, 'errors': '', 'currentblocksize': 0, 'currentblocktx': 0, 'hashespersec': 0, 'testnet': False}
'''
@my_decorator
def getmininginfo():
		return access.getmininginfo()

'''
getnewaddress
[account]
Returns a new bitcoin address for receiving payments. If [account] is specified (recommended), it is added to the address book so payments received with the address will be credited to [account].	 
N
Returns:
1J5UXyx6EyWz57nyCRGkNpLTFB8tDV7fE8
'''
@my_decorator
def getnewaddress(account="DEFAULT ACCOUNT"):
		return access.getnewaddress(account)

'''
getpeerinfo
version 0.7 Returns data about each connected node.	 
N
Returns:
[{'conntime': 1351585714, 'banscore': 0, 'addr': '192.168.1.1:8333', 'version': 60002, 'lastsend': 1351641320, 'startingheight': 205678, 'services': '00000001', 'subver': '/Satoshi:0.7.0.99/', 'lastrecv': 1351641317, 'releasetime': 0, 'inbound': False}, {'conntime': 1351593601, 'banscore': 0, 'addr': '192.168.1.2:8333', 'version': 60002, 'lastsend': 1351641320, 'startingheight': 205692, 'services': '00000001', 'subver': '/Satoshi:0.7.0.3/', 'lastrecv': 1351641320, 'releasetime': 0, 'inbound': False}]
'''
@my_decorator
def getpeerinfo():
		return access.getpeerinfo()

'''
getrawmempool
version 0.7 Returns all transaction ids in memory pool	 
N
Returns:
['fec15caa099ff0d87b38376e8236a1b503a3157b88c136620680782c8728bb10', 'fed226054c79db82f5608358ab8e41145ebfb05cee0848c560f5c0e6fb87f074', 'fefcd04d7a06eba925057ce02405856b5be375bad1d508d1722a51e96c2cd5a5', 'ff51e6605cdae2f905133e2ea435b31d7899c1a3ca8eb6bcb594dbbfe6d8a779', 'ffcc536a9e5cb3a1512ddee229b51fefa108fd82cc44c4bf55e114a6dc91688d', 'ffd413b686c1cf7c60ccfb47874b8fefd270faa54a99897c3711170335ab77e6']
'''
@my_decorator
def getrawmempool():
		return access.getrawmempool()

'''
getrawtransaction
<txid> [verbose=0]
version 0.7 Returns raw transaction representation for given transaction id.	 
N
Returns:
'''
@my_decorator
def getrawtransaction(txid, verbose=0):
		return access.getrawtransaction(txid, verbose)

'''
getreceivedbyaccount
[account] [minconf=1]
Returns the total amount received by addresses with [account] in transactions with at least [minconf] confirmations. If [account] not provided return will include all transactions to all accounts. (version 0.3.24)	 
N
Returns:
0E-8
'''
@my_decorator
def getreceivedbyaccount(account="DEFAULT ACCOUNT", minconf=0):
		return access.getreceivedbyaccount(account, minconf)

'''
getreceivedbyaddress
<bitcoinaddress> [minconf=1]
Returns the total amount received by <bitcoinaddress> in transactions with at least [minconf] confirmations. While some might consider this obvious, value reported by this only considers *receiving* transactions. It does not check payments that have been made *from* this address. In other words, this is not "getaddressbalance". Works only for addresses in the local wallet, external addresses will always show 0.	 
N
Returns:
0E-8
'''
@my_decorator
def getreceivedbyaddress(bitcoinaddress, minconf=0):
		return access.getreceivedbyaddress(bitcoinaddress, minconf)

'''
gettransaction
<txid>
Returns an object about the given transaction containing:
"amount" : total amount of the transaction
"confirmations" : number of confirmations of the transaction
"txid" : the transaction ID
"time" : time the transaction occurred
"details" - An array of objects containing:
"account"
"address"
"category"
"amount"
"fee"
N
Returns:
'''
@my_decorator
def gettransaction(txid):
		return access.gettransaction(txid)

'''
getwork
[data]
If [data] is not specified, returns formatted hash data to work on:
"midstate" : precomputed hash state after hashing the first half of the data
"data" : block data
"hash1" : formatted hash buffer for second hash
"target" : little endian hash target
If [data] is specified, tries to solve the block and returns true if it was successful.
N
Returns: 
'''
@my_decorator
def getwork(data):
		return access.getwork(data)

'''
help
[command]
List commands, or get help for a command.	 
N
Returns:
'''
@my_decorator
def help(command=""):
		return access.help(command)

'''
importprivkey
<bitcoinprivkey> [label]
Adds a private key (as returned by dumpprivkey) to your wallet.	 
Y
Returns:
'''
@my_decorator
def importprivkey(bitcoinprivkey, label="DEFAULT ACCOUNT"):
		return access.importprivkey(bitcoinprivkey, label)

'''
keypoolrefill
Fills the keypool, requires wallet passphrase to be set.	 
Y
Returns:
None
'''
@my_decorator
def keypoolrefill():
		return access.keypoolrefill()

'''
listaccounts
[minconf=1]
Returns Object that has account names as keys, account balances as values.	 
N
Returns:
{'': Decimal('0E-8'), 'Billybob': Decimal('0E-8'), 'DEFAULT ACCOUNT': Decimal('0E-8')}
'''
@my_decorator
def listaccounts(minconf=0):
		return access.listaccounts(minconf)

'''
listreceivedbyaccount
[minconf=1] [includeempty=false]
Returns an array of objects containing:
"account" : the account of the receiving addresses
"amount" : total amount received by addresses with this account
"confirmations" : number of confirmations of the most recent transaction included
N
Returns:
[{'amount': Decimal('0E-8'), 'confirmations': 0, 'account': ''}, {'amount': Decimal('0E-8'), 'confirmations': 0, 'account': 'Billybob'}]
'''
@my_decorator
def listreceivedbyaccount(minconf=0, includeempty=False):
		return access.listreceivedbyaccount(minconf, includeempty)

'''
listreceivedbyaddress
[minconf=1] [includeempty=false]
Returns an array of objects containing:
"address" : receiving address
"account" : the account of the receiving address
"amount" : total amount received by the address
"confirmations" : number of confirmations of the most recent transaction included
To get a list of accounts on the system, execute bitcoind listreceivedbyaddress 0 true
N
Returns:
[{'account': 'Billybob', 'confirmations': 0, 'amount': Decimal('0E-8'), 'address': '19b1sQojd9t5PHYdArS7hFUV7vzshNGxuk'}, {'account': 'Billybob', 'confirmations': 0, 'amount': Decimal('0E-8'), 'address': '14DDpewYAVTSKmPDLXkUs38L794eqGMuvc'}, {'account': '', 'confirmations': 0, 'amount': Decimal('0E-8'), 'address': '1AVAnwPykoPkTBsocJWiqEsZ9AxZohNeqM'}, {'account': '', 'confirmations': 0, 'amount': Decimal('0E-8'), 'address': '1J96Hgj4AvrMJkmQ7nXj8PasyyKYTapzX8'}]
'''
@my_decorator
def listreceivedbyaddress(minconf=0, includeempty=False):
		return access.listreceivedbyaddress(minconf, includeempty)

'''
listsinceblock
[blockhash] [target-confirmations]
Get all transactions in blocks since block [blockhash], or all transactions if omitted.	 
N
Returns:
'''
@my_decorator
def listsinceblock(blockhash=0, targetconfirmations=1):
		return access.listsinceblock(blockhash, targetconfirmations)

'''
listtransactions
[account] [count=10] [from=0]
Returns up to [count] most recent transactions skipping the first [from] transactions for account [account]. If [account] not provided will return recent transaction from all accounts.	 
N
Returns:
[{'timereceived': 1351652809, 'address': '17DbstW8piamyeMHURS36be2c9iGCZkiD5', 'amount': Decimal('0.10000000'), 'category': 'receive', 'txid': '2b2c0e87dc0d9e834236b79789aef8ee9790bc1d792f8910077b35569f012661', 'account': 'thisistest', 'time': 1351652809, 'confirmations': 0}]
'''
@my_decorator
def listtransactions(account, count=10, after=0):
		return access.listtransactions(account, count, after)

'''
listunspent
[minconf=1] [maxconf=999999]
version 0.7 Returns array of unspent transaction inputs in the wallet.	 
N
Returns:
[]
'''
@my_decorator
def listunspent(minconf=0, maxconf=999999):
		return access.listunspent()

'''
move
<fromaccount> <toaccount> <amount> [minconf=1] [comment]
Move from one account in your wallet to another	 
N
Returns:
True
'''
@my_decorator
def move(fromaccount, toaccount, amount, minconf=0, comment=""):
		return access.move(fromaccount,toaccount,amount,minconf,comment)

'''
sendfrom
<fromaccount> <tobitcoinaddress> <amount> [minconf=1] [comment] [comment-to]
<amount> is a real and is rounded to 8 decimal places. Will send the given amount to the given address, ensuring the account has a valid balance using [minconf] confirmations. Returns the transaction ID if successful (not in JSON object).	 
Y
Returns:
8e9425259e7d03d60a7c8e51a952dc74f6e99fdc5261ae6592da345873ede2f2
'''
@my_decorator
def sendfrom(fromaccount, tobitcoinaddress, amount, minconf=0, comment="", commentto=""):
		return access.sendfrom(fromaccount, tobitcoinaddress, amount, minconf, comment, commentto)

'''
sendmany
<fromaccount> {address:amount,...} [minconf=1] [comment]
amounts are double-precision floating point numbers	 
Y
Returns:
'''
@my_decorator
def sendmany(fromaccount, addressesamounts, minconf=0, comment=""):
		return access.sendmany(fromaccount, addressesamounts, minconf, comment)

'''
sendrawtransaction
<hexstring>
version 0.7 Submits raw transaction (serialized, hex-encoded) to local node and network.	 
N
Returns:
'''
@my_decorator
def sendrawtransaction(hexstring):
		return access.sendrawtransaction(hexstring)

'''
sendtoaddress
<bitcoinaddress> <amount> [comment] [comment-to]
<amount> is a real and is rounded to 8 decimal places. Returns the transaction ID <txid> if successful.	 
Y
Returns:
'''
@my_decorator
def sendtoaddress(bitcoinaddress, amount, comment="", commentto=""):
		return access.sendtoaddress(bitcoinaddress, amount, comment, commentto)

'''
setaccount
<bitcoinaddress> <account>
Sets the account associated with the given address. Assigning address that is already assigned to the same account will create a new address associated with that account.	 
N
Returns:
None
'''
@my_decorator
def setaccount(bitcoinaddress, account="DEFAULT ACCOUNT"):
		return access.setaccount(bitcoinaddress, account)

'''
setgenerate
<generate> [genproclimit]
<generate> is true or false to turn generation on or off.
Generation is limited to [genproclimit] processors, -1 is unlimited.	 
N
Returns:
'''
@my_decorator
def setgenerate(generate, genproclimit=1):
		return access.setgenerate(generate, genproclimit)

'''
signmessage
<bitcoinaddress> <message>
Sign a message with the private key of an address.	 
Y
Returns:
'''
@my_decorator
def signmessage(bitcoinaddress, message):
		return access.signmessage(bitcoinaddress, message)

'''
signrawtransaction
<hexstring> [{"txid":txid,"vout":n,"scriptPubKey":hex},...] [<privatekey1>,...]
version 0.7 Adds signatures to a raw transaction and returns the resulting raw transaction.	 
Y/N
Returns:
'''
@my_decorator
def signrawtransaction(txidvout, privatekeys):
		return access.signrawtransaction(txidvout, privatekeys)

'''
settxfee
<amount>
<amount> is a real and is rounded to the nearest 0.00000001	 
N
Returns:
True
'''
@my_decorator
def settxfee(amount):
		return access.settxfee(amount)
		
'''
stop
Stop bitcoin server.	 
N
Returns:
'''
@my_decorator
def stop():
		return access.stop()

'''
validateaddress
<bitcoinaddress>
Return information about <bitcoinaddress>.	 
N
Returns:
{'address': '1AVAnwPykoPkTBsocJWiqEsZ9AxZohNeqM', 'ismine': True, 'account': '', 'iscompressed': True, 'isvalid': True, 'pubkey': '03939b467ce20e52b8048339d3d7ab80f7a661f0b1c81e6c9e1ec9e6523d65d74d', 'isscript': False}
'''
@my_decorator
def validateaddress(bitcoinaddress):
		return access.validateaddress(bitcoinaddress)

'''
verifymessage
<bitcoinaddress> <signature> <message>	 Verify a signed message.	 
N
Returns:
'''
@my_decorator
def verifymessage(bitcoinaddress, signature, message):
		return access.verifymessage(bitcoinaddress, signature, message)

'''
walletlock
Removes the wallet encryption key from memory, locking the wallet. After calling this method, you will need to call walletpassphrase again before being able to call any methods which require the wallet to be unlocked.	 
N
Returns:
None
'''
@my_decorator
def walletlock():
		return access.walletlock()

'''
walletpassphrase
<passphrase> <timeout>
Stores the wallet decryption key in memory for <timeout> seconds.	 
N
Returns:
None
'''
@my_decorator
def walletpassphrase(passphrase, timeout):
		return access.walletpassphrase(passphrase, timeout)

'''
walletpassphrasechange
<oldpassphrase> <newpassphrase>
Changes the wallet passphrase from <oldpassphrase> to <newpassphrase>.	 
N
Returns:
'''
@my_decorator
def walletpassphrasechange(oldpassphrase, newpassphrase):
		return access.walletpassphrasechange(oldpassphrase, newpassphrase)

'''
transact (special call to handle change correctly)
<fromthing> <tothing> <amount>
Sends amount from fromthing to tothing.  things may be either accounts or addresses.  Change will be sent back to fromthing's account.
Y
Returns:
4db570957a740124c224f6035759ab9f484f1d32ce4b73a13ce7a3015c9c4bc8
'''
def transact(fromthing, tothing, amount):
	
	#get fromaccount from fromthing
	if (validateaddress(fromthing)['isvalid'] == True):
		fromaccount = getaccount(fromthing)
	else:
		fromaccount = fromthing
		
	#get toaddressA from tothing
	if (validateaddress(tothing)['isvalid'] == False):
		toaddressA = getaddressesbyaccount(tothing)[0]
	else:
		toaddressA = tothing
		
	#send change back to address of fromaccount
	toaddressB = getaddressesbyaccount(fromaccount)[0]
	
	balance = float(getbalance(fromaccount))
	amountA = amount
	amountB = balance -amountA -0.0005
	amountA = round(amountA,8)
	amountB = round(amountB,8)
	
	recipients = { toaddressA:amountA
                 , toaddressB:amountB
                 }

	txid = sendmany(fromaccount, recipients, minconf=0)
	return txid
	
	

		