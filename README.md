# openbazaar-go
![banner](https://i.imgur.com/iOnXDXK.png)
developertask Server Daemon in Go

[![Build Status](https://travis-ci.org/developertask/openbazaar-go.svg?branch=master)](https://travis-ci.org/developertask/openbazaar-go)
[![Coverage Status](https://coveralls.io/repos/github/developertask/openbazaar-go/badge.svg?branch=master)](https://coveralls.io/github/developertask/openbazaar-go?branch=master)
[![Go Report Card](https://goreportcard.com/badge/github.com/developertask/openbazaar-go)](https://goreportcard.com/report/github.com/developertask/openbazaar-go)

This repository contains the developertask server daemon which handles the heavy lifting for the [developertask](https://openbazaar.org/) desktop application. The server combines several technologies: A modified [IPFS](https://ipfs.io) node, which itself combines ideas from Git, BitTorrent, and Kademlia. A lightweight wallet for interacting with several cryptocurrency networks. And a JSON API which can be used by a user interface to control the node and browse the network. Find the user interface for the server at [github.com/developertask/openbazaar-desktop](https://github.com/developertask/openbazaar-desktop).

## Table of Contents

- [Install](#install)
  - [Install prebuilt packages](#install-pre-built-packages)
  - [Build from Source](#build-from-source)
- [Dependency Management](#dependency-management)
  - [IPFS Dependency](#ipfs-dependency)
- [Updating](#updating)
- [Usage](#usage)
  - [Options](#options)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Install

A typical install of developertask contains a bundle of the server daemon and user interface. If this is what you are looking for, you can find an installer at https://openbazaar.org/download. If you are looking to run the server daemon by itself or to contribute to development, see below for instructions.

### Install Pre-built Packages

The easiest way to run the server is to download a pre-built binary. You can find binaries of our latest release for each operating system [here](https://github.com/developertask/openbazaar-go/releases/).

### Build from Source

To build from source you will need to have Go installed and properly configured. Detailed instructions for installing Go and openbazaar-go on each operating system can be found in the [docs package](https://github.com/developertask/openbazaar-go/tree/master/docs).

## Dependency Management

We use [Godeps](https://github.com/tools/godep) with vendored third-party packages.

### IPFS Dependency

We are using a [fork](https://github.com/developertask/go-ipfs) of go-ipfs in the daemon. The primary changes include different protocol strings to segregate the developertask network from the main IPFS network and an increased TTL on certain types of DHT data. You can find the full diff in the readme of the forked repo. The fork is bundled in the vendor package and will be used automatically when you compile and run the server. Note that you will still see github.com/ipfs/go-ipfs import statements instead of github.com/developertask/go-ipfs despite the package being a fork. This is done to avoid a major refactor of import statements and make rebasing IPFS much easier.

## Updating

You can either pull in remote changes as normal or run `go get -u github.com/developertask/openbazaar-go`.

## Usage

You can run the server with `go run openbazaard.go start`. Ensure you are using at least version `1.10` of Golang, otherwise you might get errors while running.

### Options

```
Usage:
  openbazaard [OPTIONS] start [start-OPTIONS]

The start command starts the developertask-Server

Application Options:
  -v, --version                   Print the version number and exit

Help Options:
  -h, --help                      Show this help message

[start command options]
      -p, --password=             the encryption password if the database is encrypted
      -t, --testnet               use the test network
      -r, --regtest               run in regression test mode
      -l, --loglevel=             set the logging level [debug, info, notice, warning, error, critical]
                                  (default: debug)
      -f, --nologfiles            save logs on disk
      -a, --allowip=              only allow API connections from these IPs
      -s, --stun                  use stun on µTP IPv4
      -d, --datadir=              specify the data directory to be used
      -c, --authcookie=           turn on API authentication and use this specific cookie
      -u, --useragent=            add a custom user-agent field
      -v, --verbose               print openbazaar logs to stdout
          --torpassword=          Set the tor control password. This will override the tor password in
                                  the config.
          --tor                   Automatically configure the daemon to run as a Tor hidden service and
                                  use Tor exclusively. Requires Tor to be running.
          --dualstack             Automatically configure the daemon to run as a Tor hidden service IN
                                  ADDITION to using the clear internet. Requires Tor to be running.
                                  WARNING: this mode is not private
          --disablewallet         disable the wallet functionality of the node
          --disableexchangerates  disable the exchange rate service to prevent api queries
          --storage=              set the outgoing message storage option [self-hosted, dropbox]
                                  (default=self-hosted)
          --bitcoincash           use a Bitcoin Cash wallet in a dedicated data directory
          --zcash=                use a ZCash wallet in a dedicated data directory. To use this you must
                                  pass in the location of the zcashd binary.
```

## Documentation

Documentation of the developertask protocol has not been formalized yet. If you would like to help, please reach out on [Slack](https://openbazaar.org/slack/) or via a new issue on GitHub.

`openbazaar-go` exposes an HTTP API which permits high-level interactions on the network and the internal wallet. Find the HTTP API documentation at [https://api.docs.openbazaar.org](https://api.docs.openbazaar.org).

## Contributing

Contributions are definitely welcome! Please read the Contributing [Guidelines](https://github.com/developertask/openbazaar-go/blob/master/CONTRIBUTING.md) before starting.

## License
[MIT](https://github.com/developertask/openbazaar-go/blob/master/LICENSE).
