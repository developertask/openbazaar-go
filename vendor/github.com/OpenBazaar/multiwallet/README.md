[![Build Status](https://travis-ci.org/developertask/multiwallet.svg?branch=master)](https://travis-ci.org/developertask/multiwallet)
[![Coverage Status](https://coveralls.io/repos/github/developertask/multiwallet/badge.svg?branch=master)](https://coveralls.io/github/developertask/multiwallet?branch=master)
[![Go Report Card](https://goreportcard.com/badge/github.com/developertask/multiwallet)](https://goreportcard.com/report/github.com/developertask/multiwallet)

# multiwallet
Insight API based multi-cryptocurrency wallet

## Usage

Once your go environment is configured (https://golang.org/doc/install), you should be able to run the multiwallet like this:

```
go get -u github.com/developertask/multiwallet
cd $GOPATH/src/github.com/developertask/multiwallet

go run cmd/multiwallet/main.go -h
```

That last command will give you some subcommands you can then add to the end (in place of the `-h`):
```
Usage:
  main [OPTIONS] <command>

Help Options:
  -h, --help  Show this help message

Available commands:
  balance         get the wallet's balances
  chaintip        return the height of the chain
  currentaddress  get the current bitcoin address
  dumptables      print out the database tables
  newaddress      get a new bitcoin address
  spend           send bitcoins
  start           start the wallet
  stop            stop the wallet
  version         print the version number
```

