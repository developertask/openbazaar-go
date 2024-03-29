package main

import (
	"fmt"
	"os"
	"os/signal"
	"path/filepath"

	"github.com/developertask/openbazaar-go/cmd"
	"github.com/developertask/openbazaar-go/core"
	"github.com/ipfs/go-ipfs/repo/fsrepo"
	"github.com/jessevdk/go-flags"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("main")

type Opts struct {
	Version bool `short:"v" long:"version" description:"Print the version number and exit"`
}

var opts Opts

var parser = flags.NewParser(&opts, flags.Default)

func main() {
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		for sig := range c {
			log.Noticef("Received %s\n", sig)
			log.Info("developertask Server shutting down...")
			if core.Node != nil {
				if core.Node.MessageRetriever != nil {
					core.Node.RecordAgingNotifier.Stop()
					core.Node.InboundMsgScanner.Stop()
					close(core.Node.MessageRetriever.DoneChan)
					core.Node.MessageRetriever.Wait()
				}
				core.OfflineMessageWaitGroup.Wait()
				core.Node.PublishLock.Lock()
				core.Node.Datastore.Close()
				repoLockFile := filepath.Join(core.Node.RepoPath, fsrepo.LockFile)
				os.Remove(repoLockFile)
				core.Node.Multiwallet.Close()
				core.Node.IpfsNode.Close()
			}
			os.Exit(1)
		}
	}()

	_, err := parser.AddCommand("gencerts",
		"Generate certificates",
		"Generate self-singned certificates",
		&cmd.GenerateCertificates{})
	if err != nil {
		log.Error(err)
	}
	_, err = parser.AddCommand("init",
		"initialize a new repo and exit",
		"Initializes a new repo without starting the server",
		&cmd.Init{})
	if err != nil {
		log.Error(err)
	}
	_, err = parser.AddCommand("status",
		"get the repo status",
		"Returns the status of the repo ― Uninitialized, Encrypted, Decrypted. Also returns whether Tor is available.",
		&cmd.Status{})
	if err != nil {
		log.Error(err)
	}
	_, err = parser.AddCommand("setapicreds",
		"set API credentials",
		"The API password field in the config file takes a SHA256 hash of the password. This command will generate the hash for you and save it to the config file.",
		&cmd.SetAPICreds{})
	if err != nil {
		log.Error(err)
	}
	_, err = parser.AddCommand("start",
		"start the developertask-Server",
		"The start command starts the developertask-Server",
		&cmd.Start{})
	if err != nil {
		log.Error(err)
	}
	_, err = parser.AddCommand("encryptdatabase",
		"encrypt your database",
		"This command encrypts the database containing your bitcoin private keys, identity key, and contracts",
		&cmd.EncryptDatabase{})
	if err != nil {
		log.Error(err)
	}
	_, err = parser.AddCommand("decryptdatabase",
		"decrypt your database",
		"This command decrypts the database containing your bitcoin private keys, identity key, and contracts.\n [Warning] doing so may put your bitcoins at risk.",
		&cmd.DecryptDatabase{})
	if err != nil {
		log.Error(err)
	}
	_, err = parser.AddCommand("restore",
		"restore user data",
		"This command will attempt to restore user data (profile, listings, ratings, etc) by downloading them from the network. This will only work if the IPNS mapping is still available in the DHT. Optionally it will take a mnemonic seed to restore from.",
		&cmd.Restore{})
	if err != nil {
		log.Error(err)
	}
	if len(os.Args) > 1 && (os.Args[1] == "--version" || os.Args[1] == "-v") {
		fmt.Println(core.VERSION)
		return
	}
	if _, err := parser.Parse(); err != nil {
		os.Exit(1)
	}
}
