package core

import (
	"crypto/sha256"
	"errors"
	"fmt"
	"io/ioutil"
	"math/big"
	"os"
	"path"
	"path/filepath"

	routing "gx/ipfs/QmSY3nkMNLzh9GdbFKK5tT7YMfLpf52iUZ8ZRkr29MJaa5/go-libp2p-kad-dht"
	ma "gx/ipfs/QmTZBfrPJmjWsCvHEtX5FE6KimVJhsJg5sBbqEFYf4UZtL/go-multiaddr"
	"gx/ipfs/QmerPMzPk1mJVowm8KgmoknWa4yCYvvugMPsgWmDNUvDLW/go-multihash"

	"github.com/developertask/jsonpb"
	"github.com/developertask/openbazaar-go/ipfs"
	"github.com/developertask/openbazaar-go/pb"
	"github.com/developertask/openbazaar-go/repo"
	"golang.org/x/net/context"
)

// ModeratorPointerID  moderator ipfs multihash
var ModeratorPointerID multihash.Multihash

// ErrNoListings - no listing error
// FIXME : This is not used anywhere
var ErrNoListings = errors.New("no listings to set moderators on")

func init() {
	modHash := sha256.Sum256([]byte("moderators"))
	encoded, err := multihash.Encode(modHash[:], multihash.SHA2_256)
	if err != nil {
		log.Fatal("Error creating moderator pointer ID (multihash encode)")
	}
	mh, err := multihash.Cast(encoded)
	if err != nil {
		log.Fatal("Error creating moderator pointer ID (multihash cast)")
	}
	ModeratorPointerID = mh
}

// IsModerator - Am I a moderator?
func (n *developertaskNode) IsModerator() bool {
	profile, err := n.GetProfile()
	if err != nil {
		return false
	}
	return profile.Moderator
}

// SetSelfAsModerator - set self as a moderator
func (n *developertaskNode) SetSelfAsModerator(moderator *pb.Moderator) error {
	if moderator != nil {
		if moderator.Fee == nil {
			return errors.New("moderator must have a fee set")
		}
		if (int(moderator.Fee.FeeType) == 0 || int(moderator.Fee.FeeType) == 2) && moderator.Fee.FixedFee.BigAmount == "" && moderator.Fee.FixedFee.Amount == 0 {
			return errors.New("fixed fee must be set when using a fixed fee type")
		}

		// Update profile
		profile, err := n.GetProfile()
		if err != nil {
			return err
		}

		var currencies []string
		settingsData, _ := n.Datastore.Settings().Get()
		if settingsData.PreferredCurrencies != nil {
			currencies = append(currencies, *settingsData.PreferredCurrencies...)
		} else {
			for ct := range n.Multiwallet {
				currencies = append(currencies, ct.CurrencyCode())
			}
		}
		for _, cc := range currencies {
			currency, err := n.LookupCurrency(cc)
			if err != nil {
				return fmt.Errorf("moderator fee currency (%s) unknown: %s", cc, err)
			}
			moderator.AcceptedCurrencies = append(moderator.AcceptedCurrencies, currency.CurrencyCode().String())
		}

		profile.Moderator = true
		profile.ModeratorInfo = moderator
		err = n.UpdateProfile(&profile)
		if err != nil {
			return err
		}
	}

	// Publish pointer
	pointers, err := n.Datastore.Pointers().GetByPurpose(ipfs.MODERATOR)
	ctx := context.Background()
	if err != nil || len(pointers) == 0 {
		addr, err := ma.NewMultiaddr("/ipfs/" + n.IpfsNode.Identity.Pretty())
		if err != nil {
			return err
		}
		pointer, err := ipfs.NewPointer(ModeratorPointerID, 64, addr, []byte(n.IpfsNode.Identity.Pretty()))
		if err != nil {
			return err
		}
		go func(dht *routing.IpfsDHT, ctx context.Context, pointer ipfs.Pointer) {
			err := ipfs.PublishPointer(dht, ctx, pointer)
			if err != nil {
				log.Error(err)
			}
		}(n.DHT, ctx, pointer)
		pointer.Purpose = ipfs.MODERATOR
		err = n.Datastore.Pointers().Put(pointer)
		if err != nil {
			return err
		}
	} else {
		go func(dht *routing.IpfsDHT, ctx context.Context, pointer ipfs.Pointer) {
			err := ipfs.PublishPointer(dht, ctx, pointer)
			if err != nil {
				log.Error(err)
			}
		}(n.DHT, ctx, pointers[0])
	}
	return nil
}

// RemoveSelfAsModerator - relinquish moderatorship
func (n *developertaskNode) RemoveSelfAsModerator() error {
	// Update profile
	profile, err := n.GetProfile()
	if err != nil {
		return err
	}
	profile.Moderator = false
	err = n.UpdateProfile(&profile)
	if err != nil {
		return err
	}

	// Delete pointer from database
	err = n.Datastore.Pointers().DeleteAll(ipfs.MODERATOR)
	if err != nil {
		return err
	}
	return nil
}

// GetModeratorFee is called by the Moderator when determining their take of the dispute
func (n *developertaskNode) GetModeratorFee(transactionTotal *big.Int, txCurrencyCode string) (*big.Int, error) {
	file, err := ioutil.ReadFile(path.Join(n.RepoPath, "root", "profile.json"))
	if err != nil {
		return big.NewInt(0), err
	}
	profile := new(pb.Profile)
	err = jsonpb.UnmarshalString(string(file), profile)
	if err != nil {
		return big.NewInt(0), err
	}
	txCurrency, err := n.LookupCurrency(txCurrencyCode)
	if err != nil {
		return big.NewInt(0), fmt.Errorf("lookup dispute transaction currency (%s): %s", txCurrencyCode, err)
	}
	switch profile.ModeratorInfo.Fee.FeeType {
	case pb.Moderator_Fee_PERCENTAGE:
		feePercent := new(big.Float).Mul(big.NewFloat(float64(profile.ModeratorInfo.Fee.Percentage)), big.NewFloat(0.01))
		feePercentAmt, _ := repo.NewCurrencyValueFromBigInt(transactionTotal, txCurrency).MulBigFloat(feePercent)
		return feePercentAmt.AmountBigInt(), nil

	case pb.Moderator_Fee_FIXED:
		modFeeValue, err := repo.NewCurrencyValueFromProtobuf(profile.ModeratorInfo.Fee.FixedFee.BigAmount, profile.ModeratorInfo.Fee.FixedFee.AmountCurrency)
		if err != nil {
			return big.NewInt(0), fmt.Errorf("parse moderator fee currency: %s", err)
		}

		cc, err := n.ReserveCurrencyConverter()
		if err != nil {
			return big.NewInt(0), fmt.Errorf("preparing reserve currency converter: %s", err.Error())
		}

		convertedModFee, _, err := modFeeValue.ConvertTo(txCurrency, cc)
		if err != nil {
			return big.NewInt(0), fmt.Errorf("convert moderator fee into transaction currency (%s): %s", txCurrency.String(), err)
		}
		if convertedModFee.AmountBigInt().Cmp(transactionTotal) > 0 {
			return big.NewInt(0), errors.New("Fixed moderator fee exceeds transaction amount")
		}
		return convertedModFee.AmountBigInt(), nil

	case pb.Moderator_Fee_FIXED_PLUS_PERCENTAGE:
		modFeeValue, err := repo.NewCurrencyValueFromProtobuf(profile.ModeratorInfo.Fee.FixedFee.BigAmount, profile.ModeratorInfo.Fee.FixedFee.AmountCurrency)
		if err != nil {
			return big.NewInt(0), fmt.Errorf("parse moderator fee currency: %s", err)
		}

		cc, err := n.ReserveCurrencyConverter()
		if err != nil {
			return big.NewInt(0), fmt.Errorf("preparing reserve currency converter: %s", err.Error())
		}

		convertedModFee, _, err := modFeeValue.ConvertTo(txCurrency, cc)
		if err != nil {
			return big.NewInt(0), fmt.Errorf("convert moderator fee into transaction currency (%s): %s", txCurrency.String(), err)
		}

		feePercent := new(big.Float).Mul(big.NewFloat(float64(profile.ModeratorInfo.Fee.Percentage)), big.NewFloat(0.01))
		feePercentAmt, _ := repo.NewCurrencyValueFromBigInt(transactionTotal, txCurrency).MulBigFloat(feePercent)
		feeTotal := feePercentAmt.AddBigInt(convertedModFee.AmountBigInt())
		if feeTotal.AmountBigInt().Cmp(transactionTotal) > 0 {
			return big.NewInt(0), errors.New("Fixed moderator fee exceeds transaction amount")
		}
		return feeTotal.AmountBigInt(), nil

	default:
		return big.NewInt(0), errors.New("Unrecognized fee type")
	}
}

// SetModeratorsOnListings - set moderators for a listing
func (n *developertaskNode) SetModeratorsOnListings(moderators []string) error {
	absPath, err := filepath.Abs(path.Join(n.RepoPath, "root", "listings"))
	if err != nil {
		return err
	}
	hashes := make(map[string]string)
	walkpath := func(p string, f os.FileInfo, err error) error {
		if !f.IsDir() {
			listingJSONBytes, err := ioutil.ReadFile(p)
			if err != nil {
				return err
			}
			oldSL, err := repo.UnmarshalJSONSignedListing(listingJSONBytes)
			if err != nil {
				return err
			}
			l := oldSL.GetListing()

			if err := l.SetModerators(moderators); err != nil {
				return fmt.Errorf("settings moderator on (%s): %s", f.Name(), err.Error())
			}

			sl, err := l.Sign(n)
			if err != nil {
				return fmt.Errorf("signing listing (%s): %s", l.GetSlug(), err.Error())
			}

			fi, err := os.Create(p)
			if err != nil {
				return err
			}
			defer fi.Close()

			slBytes, err := sl.MarshalJSON()
			if err != nil {
				return fmt.Errorf("marshal signed listing (%s): %s", l.GetSlug(), err.Error())
			}

			if _, err := fi.Write(slBytes); err != nil {
				return err
			}
			hash, err := ipfs.GetHashOfFile(n.IpfsNode, p)
			if err != nil {
				return err
			}
			hashes[sl.GetSlug()] = hash

			return nil
		}
		return nil
	}

	err = filepath.Walk(absPath, walkpath)
	if err != nil {
		return err
	}

	// Update moderators and hashes on index
	updater := func(listing *repo.ListingIndexData) error {
		listing.ModeratorIDs = moderators
		if hash, ok := hashes[listing.Slug]; ok {
			listing.Hash = hash
		}
		return nil
	}
	return n.UpdateEachListingOnIndex(updater)
}

// NotifyModerators - notify moderators(peers)
func (n *developertaskNode) NotifyModerators(addedMods, removedMods []string) error {
	n.Service.WaitForReady()
	for _, mod := range addedMods {
		go func(mod string) {
			err := n.SendModeratorAdd(mod)
			if err != nil {
				log.Error(err)
			}
		}(mod)
	}
	for _, mod := range removedMods {
		go func(mod string) {
			err := n.SendModeratorRemove(mod)
			if err != nil {
				log.Error(err)
			}
		}(mod)
	}
	return nil
}
