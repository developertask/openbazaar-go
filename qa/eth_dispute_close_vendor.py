import requests
import json
import time
from collections import OrderedDict
from test_framework.test_framework import developertaskTestFramework, TestFailure


class EthDisputeCloseVendorTest(developertaskTestFramework):

    def __init__(self):
        super().__init__()
        self.num_nodes = 4

    def run_test(self):
        alice = self.nodes[1]
        bob = self.nodes[2]
        charlie = self.nodes[3]

        # generate some coins and send them to bob
        time.sleep(4)
        generated_coins = 10
        api_url = bob["gateway_url"] + "wallet/address/" + self.cointype
        r = requests.get(api_url)
        if r.status_code == 200:
            resp = json.loads(r.text)
            address = resp["address"]
        elif r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Address endpoint not found")
        else:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Unknown response")
        time.sleep(20)

        # create a profile for charlie
        pro = {"name": "Charlie"}
        api_url = charlie["gateway_url"] + "ob/profile"
        r = requests.post(api_url, data=json.dumps(pro, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Profile post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Profile POST failed. Reason: %s", resp["reason"])
        time.sleep(4)

        # make charlie a moderator
        with open('testdata/moderation.json') as listing_file:
            moderation_json = json.load(listing_file, object_pairs_hook=OrderedDict)
        api_url = charlie["gateway_url"] + "ob/moderator"
        r = requests.put(api_url, data=json.dumps(moderation_json, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Moderator post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Moderator POST failed. Reason: %s", resp["reason"])
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

        listing_json["moderators"] = [moderatorId]
        api_url = alice["gateway_url"] + "ob/listing"
        r = requests.post(api_url, data=json.dumps(listing_json, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Listing post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Listing POST failed. Reason: %s", resp["reason"])
        resp = json.loads(r.text)
        slug = resp["slug"]
        time.sleep(4)

        # get listing hash
        api_url = alice["gateway_url"] + "ob/listings/" + alice["peerId"]
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't get listing index")
        resp = json.loads(r.text)
        listingId = resp[0]["hash"]

        # bob send order
        with open('testdata/order_direct.json') as order_file:
            order_json = json.load(order_file, object_pairs_hook=OrderedDict)
        order_json["items"][0]["listingHash"] = listingId
        order_json["moderator"] = moderatorId
        order_json["paymentCoin"] = "T" + self.cointype
        api_url = bob["gateway_url"] + "ob/purchase"
        r = requests.post(api_url, data=json.dumps(order_json, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Purchase post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            self.print_logs(alice, "ob.log")
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Purchase POST failed. Reason: %s", resp["reason"])
        resp = json.loads(r.text)
        orderId = resp["orderId"]
        payment_address = resp["paymentAddress"]
        payment_amount = resp["amount"]

        # check the purchase saved correctly
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text)
        if resp["state"] != "AWAITING_PAYMENT":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob purchase saved in incorrect state")
        if resp["funded"] == True:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob incorrectly saved as funded")

        # check the sale saved correctly
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Alice")
        resp = json.loads(r.text)
        if resp["state"] != "AWAITING_PAYMENT":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice purchase saved in incorrect state")
        if resp["funded"] == True:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice incorrectly saved as funded")

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
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Spend post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Spend POST failed. Reason: %s", resp["reason"])
        time.sleep(20)

        # check bob detected payment
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text)
        if resp["state"] != "AWAITING_FULFILLMENT":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob failed to detect his payment")
        if resp["funded"] == False:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob incorrectly saved as unfunded")

        # check alice detected payment
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Alice")
        resp = json.loads(r.text)
        if resp["state"] != "AWAITING_FULFILLMENT":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice failed to detect payment")
        if resp["funded"] == False:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice incorrectly saved as unfunded")

        # alice send order fulfillment
        with open('testdata/fulfillment.json') as fulfillment_file:
            fulfillment_json = json.load(fulfillment_file, object_pairs_hook=OrderedDict)
        fulfillment_json["orderId"] = orderId
        fulfillment_json["slug"] = slug
        api_url = alice["gateway_url"] + "ob/orderfulfillment"
        r = requests.post(api_url, data=json.dumps(fulfillment_json, indent=4))
        if r.status_code == 404:
            raise TestFailure("FulfillDirectOnlineTest - FAIL: Fulfillment post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("FulfillDirectOnlineTest - FAIL: Fulfillment POST failed. Reason: %s", resp["reason"])
        time.sleep(4)

        # check bob received fulfillment
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("FulfillDirectOnlineTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text)
        if resp["state"] != "FULFILLED":
            raise TestFailure("FulfillDirectOnlineTest - FAIL: Bob failed to detect order fulfillment")

        # check alice set fulfillment correctly
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("FulfillDirectOnlineTest - FAIL: Couldn't load order from Alice")
        resp = json.loads(r.text)
        if resp["state"] != "FULFILLED":
            raise TestFailure("FulfillDirectOnlineTest - FAIL: Alice failed to order fulfillment")

        # Alice open dispute
        dispute = {
            "orderId": orderId,
            "claim": "Bastard ripped me off"
        }
        api_url = alice["gateway_url"] + "ob/opendispute/"
        r = requests.post(api_url, data=json.dumps(dispute, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: OpenDispute post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: OpenDispute POST failed. Reason: %s", resp["reason"])
        time.sleep(4)

        # Alice check dispute opened correctly
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Alice")
        resp = json.loads(r.text)
        if resp["state"] != "DISPUTED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice failed to detect his dispute resolution")

        # Bob check dispute opened correctly
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text)
        if resp["state"] != "DISPUTED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob failed to detect the dispute resolution")

        # Charlie check dispute opened correctly
        api_url = charlie["gateway_url"] + "ob/case/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load case from Clarlie")
        resp = json.loads(r.text)
        if resp["state"] != "DISPUTED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Charlie failed to detect the dispute resolution")

        # Charlie close dispute
        dispute_resolution = {
            "OrderID": orderId,
            "Resolution": "I'm siding with Bob",
            "BuyerPercentage": 0,
            "VendorPercentage": 100
        }
        api_url = charlie["gateway_url"] + "ob/closedispute/"
        r = requests.post(api_url, data=json.dumps(dispute_resolution, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: CloseDispute post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: CloseDispute POST failed. Reason: %s", resp["reason"])
        time.sleep(4)

        # Alice check dispute closed correctly
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Alice")
        resp = json.loads(r.text)
        if resp["state"] != "DECIDED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice failed to detect the dispute resolution")

        # Bob check dispute closed correctly
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text, object_pairs_hook=OrderedDict)
        if resp["state"] != "DECIDED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob failed to detect the dispute resolution")

        # Charlie check dispute closed correctly
        api_url = charlie["gateway_url"] + "ob/case/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load case from Clarlie")
        resp = json.loads(r.text, object_pairs_hook=OrderedDict)
        if resp["state"] != "RESOLVED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Charlie failed to detect the dispute resolution")

        # Alice release funds
        release = {
            "OrderID": orderId,
        }
        api_url = alice["gateway_url"] + "ob/releasefunds/"
        r = requests.post(api_url, data=json.dumps(release, indent=4))
        if r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: ReleaseFunds post endpoint not found")
        elif r.status_code != 200:
            resp = json.loads(r.text)
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: ReleaseFunds POST failed. Reason: %s", resp["reason"])
        time.sleep(20)

        time.sleep(2)

        # Check alice received payout
        api_url = alice["gateway_url"] + "wallet/balance/T" + self.cointype
        r = requests.get(api_url)
        if r.status_code == 200:
            resp = json.loads(r.text)
            confirmed = int(resp["confirmed"])
            #unconfirmed = int(resp["unconfirmed"])
            if confirmed <= 0:
                raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice failed to detect dispute payout")
        elif r.status_code == 404:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Receive coins endpoint not found")
        else:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Unknown response")

        # Alice check payout transaction recorded
        api_url = alice["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Alice")
        resp = json.loads(r.text, object_pairs_hook=OrderedDict)
        if len(resp["paymentAddressTransactions"]) != 2:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice failed to record payout transaction")
        if resp["state"] != "RESOLVED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Alice failed to set state to RESOLVED")

        time.sleep(30)
        # Bob check payout transaction recorded
        api_url = bob["gateway_url"] + "ob/order/" + orderId
        r = requests.get(api_url)
        if r.status_code != 200:
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Couldn't load order from Bob")
        resp = json.loads(r.text, object_pairs_hook=OrderedDict)
        print("bobs paymnt txns : ", len(resp["paymentAddressTransactions"]))
        print("state : ", resp["state"])
        ##if len(resp["paymentAddressTransactions"]) != 2:
        ##    raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob failed to record payout transaction")
        if resp["state"] != "RESOLVED":
            raise TestFailure("EthDisputeCloseVendorTest - FAIL: Bob failed to set state to RESOLVED")

        print("EthDisputeCloseVendorTest - PASS")


if __name__ == '__main__':
    print("Running EthDisputeCloseVendorTest")
    EthDisputeCloseVendorTest().main(["--regtest", "--disableexchangerates"])
