SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE IF NOT EXISTS `TEST_TABLE_FAUCET_PAYOUTS` (
  `transaction_id` varchar(64) NOT NULL,
  `username` varchar(16) NOT NULL,
  `address` varchar(64) DEFAULT NULL,
  `amount` int(10) unsigned DEFAULT '0',
  `timestamp` int(10) unsigned DEFAULT '0',
  UNIQUE KEY `transaction_id` (`transaction_id`,`username`,`address`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `TEST_TABLE_RECENT` (
  `type` varchar(64) NOT NULL,
  `timestamp` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastallowedsubredditsfetched', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastallowedsubredditsfetchedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastbackuptime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastbannedusersfetched', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastbannedusersfetchedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastcommentevaluated', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastcommentevaluatedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastexchangeratefetched', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastexchangeratefetchedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastfriendcommentevaluated', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastfriendcommentevaluatedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastfriendsofbitcointipfetched', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastfriendsofbitcointipfetchedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastmessageevaluated', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastmessageevaluatedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastpendingnotified', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastpendingnotifiedtime', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastpendingupdated', 0);
INSERT INTO `TEST_TABLE_RECENT` (`type`, `timestamp`) VALUES('lastpendingupdatedtime', 0);

CREATE TABLE IF NOT EXISTS `TEST_TABLE_TOSUBMIT` (
  `tosubmit_id` varchar(16) NOT NULL,
  `type` varchar(32) NOT NULL,
  `replyto` varchar(32) NOT NULL,
  `subject` text NOT NULL,
  `text` text NOT NULL,
  `captchaid` varchar(16) DEFAULT NULL,
  `captchasol` varchar(16) DEFAULT NULL,
  `sent` int(10) unsigned NOT NULL DEFAULT '0',
  `timestamp` int(10) unsigned NOT NULL DEFAULT '0',
  UNIQUE KEY `tosubmit_id` (`tosubmit_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `TEST_TABLE_TRANSACTIONS` (
  `transaction_id` varchar(64) NOT NULL,
  `sender_username` varchar(16) NOT NULL,
  `sender_address` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `receiver_username` varchar(16) NOT NULL,
  `receiver_address` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `amount_BTC` int(10) NOT NULL,
  `amount_USD` int(10) NOT NULL,
  `type` varchar(32) NOT NULL,
  `url` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `subreddit` varchar(32) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `verify` tinyint(1) NOT NULL DEFAULT '0',
  `statusmessage` text NOT NULL,
  `status` varchar(16) NOT NULL,
  UNIQUE KEY `transaction_id` (`transaction_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `TEST_TABLE_USERS` (
  `userid` varchar(32) NOT NULL,
  `username` varchar(16) NOT NULL,
  `address` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `balance` int(10) NOT NULL DEFAULT '0',
  `datejoined` int(11) NOT NULL,
  `giftamount` int(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`userid`),
  UNIQUE KEY `username` (`username`,`address`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

