#!/usr/bin/env python

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Numeric, UnicodeText

class BitcointipDatabase:
  
  metadata = MetaData()
  
  test_table_faucet_payouts = Table(
    'TEST_TABLE_FAUCET_PAYOUTS',
    metadata,
    Column("transaction_id", String(64)),
    Column("username", String(16)),
    Column("address", String(64)),
    Column("amount", Numeric(10)),
    Column("timestamp", Integer()),
  )

  test_table_recent = Table(
    'TEST_TABLE_RECENT',
    metadata,
    Column("type", String(64)),
    Column("timestamp", Integer()),
  )

  test_table_tosubmit = Table(
    'TEST_TABLE_TOSUBMIT',
    metadata,
    Column("tosubmit_id", String(16)),
    Column("type", String(32)),
    Column("replyto", String(32)),
    Column("subject", UnicodeText()),
    Column("text", UnicodeText()),
    Column("captchaid", String(16)),
    Column("captchasol", String(16)),
    Column("sent", Integer()),
    Column("timestamp", Integer()),
  )

  test_table_transactions = Table(
    'TEST_TABLE_TRANSACTIONS',
    metadata,
    Column("transaction_id", String(64)),
    Column("sender_username", String(16)),
    Column("sender_address", String(64)),
    Column("receiver_username", String(16)),
    Column("receiver_address", String(64)),
    Column("amount_BTC", Numeric(10)),
    Column("amount_USD", Numeric(10)),
    Column("type", String(32)),
    Column("url", String(32)),
    Column("subreddit", String(32)),
    Column("timestamp", Integer()),
    Column("verify", Integer()),
    Column("statusmessage", UnicodeText()),
    Column("status", String(16)),
  )

  test_table_users = Table(
    'TEST_TABLE_USERS',
    metadata,
    Column("userid", String(32)),
    Column("username", String(16)),
    Column("address", String(64)),
    Column("balance", Numeric(10)),
    Column("datejoined", Integer()),
    Column("giftamount", Numeric(10)),
  )
  
  def __init__(self, dsn_url):
    '''Pass a DSN URL conforming to the SQLAlchemy API'''
    self.dsn_url = dsn_url
  
  def connect(self):
    '''Return a connection object'''
    engine = create_engine(self.dsn_url)
    self.metadata.create_all(engine)
    return engine