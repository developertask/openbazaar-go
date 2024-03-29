package migrations_test

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"path"
	"testing"

	"github.com/developertask/openbazaar-go/repo/migrations"
)

func TestMigration011(t *testing.T) {
	// Setup
	err := os.Mkdir("./datastore", os.ModePerm)
	if err != nil {
		t.Log(err)
	}
	defer os.RemoveAll("./datastore")
	defer testMigration011SetupFixtures(t)()

	// Test migration up
	var m migrations.Migration011
	err = m.Up(".", "", true)
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll("./repover")
	assertCorrectRepoVer(t, "./repover", "12")
	assertCorrectFileContents(t, path.Join(".", "root", "listings.json"), testMigration011ExpectedListingIndexAfterMigration)

	// Test migration down
	err = m.Down(".", testMigration009Password, true)
	if err != nil {
		t.Fatal(err)
	}
	assertCorrectRepoVer(t, "./repover", "11")
}

func testMigration011SetupFixtures(t *testing.T) func() {
	if err := os.Mkdir(path.Join(".", "root"), os.ModePerm); err != nil {
		t.Fatal(err)
	}
	if err := os.Mkdir(path.Join(".", "root", "listings"), os.ModePerm); err != nil {
		t.Fatal(err)
	}

	var (
		listingsIndexPath = path.Join(".", "root", "listings.json")
		listing1Path      = path.Join(".", "root", "listings", "slug-1.json")
		listing2Path      = path.Join(".", "root", "listings", "slug-2.json")
		listing1Fixture   = migrations.Migration011_listing{
			Listing: migrations.Migration011_listing_listing{
				ModeratorIDs: []string{"a", "b"},
			},
		}
		listing2Fixture = migrations.Migration011_listing{
			Listing: migrations.Migration011_listing_listing{
				ModeratorIDs: []string{"c", "d", "e"},
			},
		}
	)

	if err := ioutil.WriteFile(listingsIndexPath, []byte(testMigration011ExpectedListingIndexBeforeMigration), os.ModePerm); err != nil {
		t.Fatal(err)
	}

	listingJSON, err := json.Marshal(listing1Fixture)
	if err != nil {
		t.Fatal(err)
	}
	if err = ioutil.WriteFile(listing1Path, listingJSON, os.ModePerm); err != nil {
		t.Fatal(err)
	}

	listingJSON, err = json.Marshal(listing2Fixture)
	if err != nil {
		t.Fatal(err)
	}
	if err = ioutil.WriteFile(listing2Path, listingJSON, os.ModePerm); err != nil {
		t.Fatal(err)
	}

	return func() {
		os.RemoveAll("./root")
	}
}

var testMigration011ExpectedListingIndexAfterMigration = `[
    {
        "acceptedCurrencies": [
            "TBTC"
        ],
        "averageRating": 5,
        "categories": [
            "category-1"
        ],
        "coinType": "BTC",
        "contractType": "PHYSICAL_GOOD",
        "description": "test",
        "freeShipping": [
            "US"
        ],
        "hash": "Listing1",
        "language": "en",
        "moderators": [
            "a",
            "b"
        ],
        "nsfw": false,
        "price": {
            "amount": 10,
            "currencyCode": "BCH"
        },
        "ratingCount": 999,
        "shipsTo": [
            "US"
        ],
        "slug": "slug-1",
        "thumbnail": {
            "medium": "c",
            "small": "b",
            "tiny": "a"
        },
        "title": "Listing 1"
    },
    {
        "acceptedCurrencies": [
            "TBTC"
        ],
        "averageRating": 5,
        "categories": [
            "category-1",
            "category-2"
        ],
        "coinType": "BTC",
        "contractType": "PHYSICAL_GOOD",
        "description": "test",
        "freeShipping": [
            "US"
        ],
        "hash": "Listing2",
        "language": "en",
        "moderators": [
            "c",
            "d",
            "e"
        ],
        "nsfw": true,
        "price": {
            "amount": 10,
            "currencyCode": "BCH"
        },
        "ratingCount": 999,
        "shipsTo": [
            "US"
        ],
        "slug": "slug-2",
        "thumbnail": {
            "medium": "c",
            "small": "b",
            "tiny": "a"
        },
        "title": "Listing 2"
    }
]`

var testMigration011ExpectedListingIndexBeforeMigration = `[
    {
        "hash": "Listing1",
        "slug": "slug-1",
        "title": "Listing 1",
        "categories": [
            "category-1"
        ],
        "nsfw": false,
        "coinType": "BTC",
        "contractType": "PHYSICAL_GOOD",
        "description": "test",
        "thumbnail": {
            "medium": "c",
            "small": "b",
            "tiny": "a"
        },
        "price": {
            "amount": 10,
            "currencyCode": "BCH"
        },
        "shipsTo": ["US"],
        "freeShipping": ["US"],
        "language": "en",
        "averageRating": 5,
        "ratingCount": 999,
        "moderators": null,
        "acceptedCurrencies": [
            "TBTC"
        ]
    },
    {
        "hash": "Listing2",
        "slug": "slug-2",
        "title": "Listing 2",
        "categories": [
            "category-1",
            "category-2"
        ],
        "nsfw": true,
        "coinType": "BTC",
        "contractType": "PHYSICAL_GOOD",
        "description": "test",
        "thumbnail": {
            "medium": "c",
            "small": "b",
            "tiny": "a"
        },
        "price": {
            "amount": 10,
            "currencyCode": "BCH"
        },
        "shipsTo": ["US"],
        "freeShipping": ["US"],
        "language": "en",
        "averageRating": 5,
        "ratingCount": 999,
        "moderators": null,
        "acceptedCurrencies": [
            "TBTC"
        ]
    }
]`
