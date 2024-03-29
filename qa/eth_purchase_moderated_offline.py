import requests
import json
import time
from collections import OrderedDict
from test_framework.test_framework import developertaskTestFramework, TestFailure


class EthPurchaseModeratedOfflineTest(developertaskTestFramework):

    def __init__(self):
        super().__init__()
        self.num_nodes = 4

    def run_test(self):
        alice = self.nodes[1]
        bob = self.nodes[2]
        charlie = self.nodes[3]

        # generate some coins and send them to bob
        time.sleep(4)
        api_url = bob["gateway_url"] + "wallet/address/" + self.cointype
        r = requests.get(api_url)
        if r.status_code == 200:
            resp = json.loads(r.text)
            address = resp["address"]
        elif r.status_code == 404:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Address endpoint not found")
        else:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Unknown response")
        time.sleep(20)

        # create a profile for charlie
        pro = {"name": "Charlie"}
        api_url = charlie["gateway_url"] + "ob/profile"
        r = requests.post(api_url, data=json.dumps(pro, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Profile post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Profile POST failed. Reason: %s", resp["reason"])
        time.sleep(4)

        # make charlie a moderator
        with open('testdata/moderation.json') as listing_file:
            moderation_json = json.load(listing_file, object_pairs_hook=OrderedDict)
        api_url = charlie["gateway_url"] + "ob/moderator"
        r = requests.put(api_url, data=json.dumps(moderation_json, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Moderator post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Moderator POST failed. Reason: %s", resp["reason"])
        moderatorId = charlie["peerId"]
        time.sleep(4)

        # post profile for alice
        with open('testdata/profile.json') as profile_file:
            profile_json = json.load(profile_file, object_pairs_hook=OrderedDict)
        api_url = alice["gateway_url"] + "ob/profile"
        requests.post(api_url, data=json.dumps(profile_json, indent=4))

        # post listing to alice
        with open('testdata/eth_listing.json') as listing_file:
            listing_json = json.load(listing_file, object_pairs_hook=OrderedDict)
        listing_json["item"]["priceCurrency"]["code"] = "T" + self.cointype
        listing_json["metadata"]["acceptedCurrencies"] = ["T" + self.cointype]

        api_url = alice["gateway_url"] + "ob/listing"
        listing_json["moderators"] = [moderatorId]
        r = requests.post(api_url, data=json.dumps(listing_json, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Listing post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Listing POST failed. Reason: %s", resp["reason"])
        time.sleep(4)

        # get listing hash
        api_url = alice["gateway_url"] + "ob/listings/" + alice["peerId"]
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Couldn't get listing index")
        resp = json.loads(r.text)
        listingId = resp[0]["hash"]

        # bob fetch listing to cache
        api_url = bob["gateway_url"] + "ipfs/" + listingId
        requests.get(api_url)

        # shutdown alice
        api_url = alice["gateway_url"] + "ob/shutdown"
        requests.post(api_url, data="")
        time.sleep(10)

        # bob send order
        with open('testdata/order_direct.json') as order_file:
            order_json = json.load(order_file, object_pairs_hook=OrderedDict)
        order_json["items"][0]["listingHash"] = listingId
        order_json["moderator"] = moderatorId
        order_json["paymentCoin"] = "T" + self.cointype
        api_url = bob["gateway_url"] + "ob/purchase"
        r = requests.post(api_url, data=json.dumps(order_json, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Purchase post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Purchase POST failed. Reason: %s", resp["reason"])
        resp = json.loads(r.text)
        orderId = resp["orderId"]
        payment_address = resp["paymentAddress"]
        payment_amount = resp["amount"]
        if resp["vendorOnline"] == True:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Purchase returned vendor is online")

        # check the purchase saved correctly
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text)
        if resp["state"] != "AWAITING_PAYMENT":
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Bob purchase saved in incorrect state")
        if resp["funded"] == True:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Bob incorrectly saved as funded")

        # fund order
        spend = {
            "currencyCode": "T" + self.cointype,
            "address": payment_address,
            "amount": payment_amount["amount"],
            "feeLevel": "NORMAL",
            "requireAssociateOrder": True,
            "orderID": orderId
        }
        api_url = bob["gateway_url"] + "ob/orderspend"
        r = requests.post(api_url, data=json.dumps(spend, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Spend post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Purchase POST failed. Reason: %s", resp["reason"])
        time.sleep(20)

        # check bob detected payment
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text)
        if len(resp["paymentAddressTransactions"]) <= 0:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Bob failed to detect his payment")
        if resp["funded"] == False:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Bob incorrectly saved as unfunded")
        if resp["state"] != "PENDING":
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Bob purchase saved in incorrect state")

        # startup alice again
        self.start_node(alice)
        time.sleep(80)

        # check alice detected order and payment
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Couldn't load order from Alice %s", r.status_code)
        resp = json.loads(r.text)
        if resp["state"] != "PENDING":
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Alice failed to detect initial payment")
        if resp["funded"] == False:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Alice incorrectly saved as unfunded")

        # check alice balance is zero
        api_url = alice["gateway_url"] + "wallet/balance/T" + self.cointype
        r = requests.get(api_url)
        if r.status_code == 200:
            resp = json.loads(r.text)
            confirmed = int(resp["confirmed"])
            unconfirmed = int(resp["unconfirmed"])
            ##if confirmed + unconfirmed > 0:
            ##    raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Alice should have zero balance at this point")
        else:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Failed to query Alice's balance")
        time.sleep(1)

        # alice confirm offline order
        api_url = alice["gateway_url"] + "ob/orderconfirmation"
        oc = {
            "orderId": orderId,
            "reject": False
        }
        r = requests.post(api_url, data=json.dumps(oc, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Order confirmation post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthPurchaseModeratedOfflineTest - FAIL: Purchase POST failed. Reason: %s", resp["reason"])
        time.sleep(10)

        # check bob detected order confirmation
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("PurchaseDirectOnlineTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text)
        if resp["state"] != "AWAITING_FULFILLMENT":
            raise TestFailure("PurchaseDirectOnlineTest - FAIL: Bob failed to set state correctly")
        if resp["funded"] == False:
            raise TestFailure("PurchaseDirectOnlineTest - FAIL: Bob incorrectly saved as unfunded")

        # check alice set state correctly
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("PurchaseDirectOnlineTest - FAIL: Couldn't load order from Alice")
        resp = json.loads(r.text)
        if resp["state"] != "AWAITING_FULFILLMENT":
            raise TestFailure("PurchaseDirectOnlineTest - FAIL: Alice failed to detect payment")
        if resp["funded"] == False:
            raise TestFailure("PurchaseDirectOnlineTest - FAIL: Alice incorrectly saved as unfunded")

        print("EthPurchaseModeratedOfflineTest - PASS")


if __name__ == '__main__':
    print("Running EthPurchaseModeratedOfflineTest")
    EthPurchaseModeratedOfflineTest().main(["--regtest", "--disableexchangerates"])
