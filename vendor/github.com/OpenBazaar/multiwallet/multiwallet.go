package multiwallet

import (
	"errors"
	"strings"
	"time"

	eth "github.com/developertask/go-ethwallet/wallet"
	"github.com/developertask/multiwallet/bitcoin"
	"github.com/developertask/multiwallet/bitcoincash"
	"github.com/developertask/multiwallet/client/blockbook"
	"github.com/developertask/multiwallet/config"
	"github.com/developertask/multiwallet/gleecbtc"
	"github.com/developertask/multiwallet/service"
	"github.com/developertask/multiwallet/zcash"
	"github.com/developertask/wallet-interface"
	"github.com/btcsuite/btcd/chaincfg"
	"github.com/op/go-logging"
	"github.com/tyler-smith/go-bip39"
)

var log = logging.MustGetLogger("multiwallet")

var UnsuppertedCoinError = errors.New("multiwallet does not contain an implementation for the given coin")

type MultiWallet map[wallet.CoinType]wallet.Wallet

func NewMultiWallet(cfg *config.Config) (MultiWallet, error) {
	log.SetBackend(logging.AddModuleLevel(cfg.Logger))
	service.Log = log
	blockbook.Log = log

	if cfg.Mnemonic == "" {
		ent, err := bip39.NewEntropy(128)
		if err != nil {
			return nil, err
		}
		mnemonic, err := bip39.NewMnemonic(ent)
		if err != nil {
			return nil, err
		}
		cfg.Mnemonic = mnemonic
		cfg.CreationDate = time.Now()
	}

	multiwallet := make(MultiWallet)
	var err error
	for _, coin := range cfg.Coins {
		var w wallet.Wallet
		switch coin.CoinType {
		case wallet.Bitcoin:
			w, err = bitcoin.NewBitcoinWallet(coin, cfg.Mnemonic, cfg.Params, cfg.Proxy, cfg.Cache, cfg.DisableExchangeRates)
			if err != nil {
				return nil, err
			}
			if cfg.Params.Name == chaincfg.MainNetParams.Name {
				multiwallet[wallet.Bitcoin] = w
			} else {
				multiwallet[wallet.TestnetBitcoin] = w
			}
		case wallet.BitcoinCash:
			w, err = bitcoincash.NewBitcoinCashWallet(coin, cfg.Mnemonic, cfg.Params, cfg.Proxy, cfg.Cache, cfg.DisableExchangeRates)
			if err != nil {
				return nil, err
			}
			if cfg.Params.Name == chaincfg.MainNetParams.Name {
				multiwallet[wallet.BitcoinCash] = w
			} else {
				multiwallet[wallet.TestnetBitcoinCash] = w
			}
		case wallet.Zcash:
			w, err = zcash.NewZCashWallet(coin, cfg.Mnemonic, cfg.Params, cfg.Proxy, cfg.Cache, cfg.DisableExchangeRates)
			if err != nil {
				return nil, err
			}
			if cfg.Params.Name == chaincfg.MainNetParams.Name {
				multiwallet[wallet.Zcash] = w
			} else {
				multiwallet[wallet.TestnetZcash] = w
			}
		case wallet.Gleecbtc:
			w, err = gleecbtc.NewGleecbtcWallet(coin, cfg.Mnemonic, cfg.Params, cfg.Proxy, cfg.Cache, cfg.DisableExchangeRates)
			if err != nil {
				return nil, err
			}
			if cfg.Params.Name == chaincfg.MainNetParams.Name {
				multiwallet[wallet.Gleecbtc] = w
			} else {
				multiwallet[wallet.TestnetGleecbtc] = w
			}
		case wallet.Ethereum:
			w, err = eth.NewEthereumWallet(coin, cfg.Params, cfg.Mnemonic, cfg.Proxy)
			if err != nil {
				return nil, err
			}
			if cfg.Params.Name == chaincfg.MainNetParams.Name {
				multiwallet[wallet.Ethereum] = w
			} else {
				multiwallet[wallet.TestnetEthereum] = w
			}
		}
	}
	return multiwallet, nil
}

func (w *MultiWallet) Start() {
	for _, wallet := range *w {
		wallet.Start()
	}
}

func (w *MultiWallet) Close() {
	for _, wallet := range *w {
		wallet.Close()
	}
}

func (w *MultiWallet) WalletForCurrencyCode(currencyCode string) (wallet.Wallet, error) {
	for _, wl := range *w {
		if strings.EqualFold(wl.CurrencyCode(), currencyCode) || strings.EqualFold(wl.CurrencyCode(), "T"+currencyCode) {
			return wl, nil
		}
	}
	return nil, UnsuppertedCoinError
}
