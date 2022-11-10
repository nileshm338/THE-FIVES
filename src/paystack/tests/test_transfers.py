import pytest
from fixture_data import transfers as transfers_list
from unittest import TestCase, mock
from paystack.utils import PaystackAPI, MockRequest
from paystack.api.transfer import filter_result

PAYSTACK_API_URL = "https://api.paystack.co"


def test_all_transfer_filters_by_status():
    filters = {"status": "failed"}
    assert len(filter_result(transfers_list, filters)) == 2


def test_all_transfer_by_created():
    assert (
        len(
            filter_result(
                transfers_list,
                {"date_kind": "created", "_from": "2019-03-2", "to": "2019-03-4"},
            )
        )
        == 1
    )


def test_all_transfers_by_updated():
    result = filter_result(
        transfers_list,
        {"date_kind": "updated", "_from": "2019-03-2", "to": "2019-03-6"},
    )
    assert len(result) == 2


def test_all_transfers_by_recipient_code():
    assert (
        len(
            filter_result(
                transfers_list,
                {"r_kind": "recipient_code", "recipient": "RCP_rvqc1kyc3isc4ys"},
            )
        )
        == 1
    )


def test_all_transfers_by_recipient_name():
    assert (
        len(
            filter_result(
                transfers_list,
                {"r_kind": "recipient_name", "recipient": "Amarachi Olusina"},
            )
        )
        == 1
    )


def test_all_transfers_by_recipient_account_number():
    assert (
        len(
            filter_result(
                transfers_list,
                {"r_kind": "recipient_account", "recipient": "0108996727"},
            )
        )
        == 1
    )


class TestTransferTestCase(TestCase):
    def setUp(self):
        self.api = PaystackAPI(
            public_key="public_key",
            secret_key="secret_key",
            django=False,
            base_url=PAYSTACK_API_URL,
        )
        self.headers = {
            "Authorization": "Bearer {}".format(self.api.secret_key),
            "Content-Type": "application/json",
        }

    @mock.patch("requests.post")
    def test_create_recipient_success(self, mock_post):
        result = {
            "status": True,
            "message": "Recipient created",
            "data": {
                "type": "nuban",
                "name": "Zombie",
                "description": "Zombier",
                "metadata": {"job": "Flesh Eater"},
                "domain": "test",
                "details": {
                    "account_number": "0100000010",
                    "account_name": None,
                    "bank_code": "044",
                    "bank_name": "Access Bank",
                },
                "currency": "NGN",
                "recipient_code": "RCP_1i2k27vk4suemug",
                "active": True,
                "id": 27,
                "createdAt": "2017-02-02T19:35:33.686Z",
                "updatedAt": "2017-02-02T19:35:33.686Z",
            },
        }
        mock_post.return_value = MockRequest(result)
        response = self.api.transfer_api.create_recipient(
            "Jamie Novak", "01000000010", "Access Bank"
        )
        mock_post.assert_called_once_with(
            "{}/transferrecipient".format(self.api.base_url),
            json={
                "type": "nuban",
                "name": "Jamie Novak",
                "description": "Jamie Novak",
                "account_number": "01000000010",
                "bank_code": "044",
                "currency": "NGN",
            },
            headers=self.headers,
        )
        self.assertTrue(response[0])
        self.assertEqual(response[1], result["message"])
        self.assertEqual(response[2], result["data"])

    @mock.patch("requests.post")
    def test_create_recipient_fail(self, mock_post):
        mock_post.return_value = MockRequest(
            {"status": False, "message": "Account number is invalid"}, status_code=400
        )
        result = self.api.transfer_api.create_recipient(
            "Jamie Novak", "01000000010", "Access Bank"
        )

        self.assertFalse(result[0])
        self.assertEqual(result[1], "Account number is invalid")

    @mock.patch("requests.post")
    def test_initialize_transfer_success(self, mock_post):
        result = {
            "status": True,
            "message": "Transfer requires OTP to continue",
            "data": {
                "integration": 100073,
                "domain": "test",
                "amount": 3794800,
                "currency": "NGN",
                "source": "balance",
                "reason": "Calm down",
                "recipient": 28,
                "status": "otp",
                "transfer_code": "TRF_1ptvuv321ahaa7q",
                "id": 14,
                "createdAt": "2017-02-03T17:21:54.508Z",
                "updatedAt": "2017-02-03T17:21:54.508Z",
            },
        }
        mock_post.return_value = MockRequest(result)
        response = self.api.transfer_api.initialize_transfer(
            37948, "RCP_gx2wn530m0i3w3m", "Calm down"
        )
        mock_post.assert_called_once_with(
            "{}/transfer".format(self.api.base_url),
            json={
                "source": "balance",
                "reason": "Calm down",
                "amount": 3794800,
                "recipient": "RCP_gx2wn530m0i3w3m",
            },
            headers=self.headers,
        )
        self.assertTrue(response[0])
        self.assertEqual(response[1], result["message"])
        self.assertEqual(response[2], result["data"])

    @mock.patch("requests.post")
    def test_initialize_transfer_failed(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                "message": "The customer specified has no saved authorizations",
            },
            status_code=400,
        )
        result = self.api.transfer_api.initialize_transfer(
            37948, "RCP_gx2wn530m0i3w3m", "Calm down"
        )

        self.assertFalse(result[0])
        self.assertEqual(
            result[1], "The customer specified has no saved authorizations"
        )

    @mock.patch("requests.post")
    def test_verify_transfer_success(self, mock_post):
        result = {}
        mock_post.return_value = MockRequest(result)
        response = self.api.transfer_api.verify_transfer("TRF_2x5j67tnnw1t98k", "1001")
        mock_post.assert_called_once_with(
            "{}/transfer/finalize_transfer".format(self.api.base_url),
            json={"transfer_code": "TRF_2x5j67tnnw1t98k", "otp": "1001"},
            headers=self.headers,
        )
        self.assertTrue(response[0])

    @mock.patch("requests.post")
    def test_verify_transfer_failed(self, mock_post):
        mock_post.return_value = MockRequest(
            {"status": False, "message": "Transfer is not currently awaiting OTP"},
            status_code=400,
        )
        result = self.api.transfer_api.verify_transfer("TRF_2x5j67tnnw1t98k", "1001")

        self.assertFalse(result[0])
        self.assertEqual(result[1], "Transfer is not currently awaiting OTP")

    @mock.patch("requests.get")
    def test_get_transfer_success(self, mock_get):
        result = {
            "status": True,
            "message": "Transfer retrieved",
            "data": {
                "recipient": {
                    "domain": "test",
                    "type": "nuban",
                    "currency": "NGN",
                    "name": "Flesh",
                    "details": {
                        "account_number": "olounje",
                        "account_name": None,
                        "bank_code": "044",
                        "bank_name": "Access Bank",
                    },
                    "metadata": None,
                    "recipient_code": "RCP_2x5j67tnnw1t98k",
                    "active": True,
                    "id": 28,
                    "integration": 100073,
                    "createdAt": "2017-02-02T19:39:04.000Z",
                    "updatedAt": "2017-02-02T19:39:04.000Z",
                },
                "domain": "test",
                "amount": 4400,
                "currency": "NGN",
                "source": "balance",
                "source_details": None,
                "reason": "Redemption",
                "status": "pending",
                "failures": None,
                "transfer_code": "TRF_2x5j67tnnw1t98k",
                "id": 14938,
                "createdAt": "2017-02-03T17:21:54.000Z",
                "updatedAt": "2017-02-03T17:21:54.000Z",
            },
        }
        mock_get.return_value = MockRequest(result)
        response = self.api.transfer_api.get_transfer("TRF_2x5j67tnnw1t98k")
        mock_get.assert_called_once_with(
            "{}/transfer/{}".format(self.api.base_url, "TRF_2x5j67tnnw1t98k"),
            headers=self.headers,
        )
        self.assertTrue(response[0])
        self.assertEqual(response[1], result["message"])
        self.assertEqual(response[2], result["data"])

    @mock.patch("requests.get")
    def test_get_transfer_failed(self, mock_get):
        mock_get.return_value = MockRequest(
            {"status": False, "message": "Transfer ID/code specified is invalid"},
            status_code=400,
        )
        result = self.api.transfer_api.get_transfer("TRF_2x5j67tnnw1t98k")

        self.assertFalse(result[0])
        self.assertEqual(result[1], "Transfer ID/code specified is invalid")

    @mock.patch("requests.post")
    def test_transfer_bulk_success(self, mock_post):
        result = {"status": True, "message": "2 transfers queued."}
        mock_post.return_value = MockRequest(result)
        transfers = [{"amount": 500, "recipient": "RCP_gx2wn530m0i3w3m"}]
        transform = [
            {"amount": x["amount"] * 100, "recipient": x["recipient"]}
            for x in transfers
        ]
        response = self.api.transfer_api.bulk_transfer(transfers)
        json_data = {"currency": "NGN", "source": "balance", "transfers": transform}
        mock_post.assert_called_once_with(
            "{}/transfer/bulk".format(self.api.base_url),
            json=json_data,
            headers=self.headers,
        )
        self.assertTrue(response[0])
        self.assertEqual(response[1], result["message"])

    @mock.patch("requests.post")
    def test_transfer_bulk_failed(self, mock_post):
        mock_post.return_value = MockRequest(
            {
                "status": False,
                "message": "The customer specified has no saved authorizations",
            },
            status_code=400,
        )
        transfers = [{"amount": 500, "recipient": "RCP_gx2wn530m0i3w3m"}]

        result = self.api.transfer_api.bulk_transfer(transfers)

        self.assertFalse(result[0])
        self.assertEqual(
            result[1], "The customer specified has no saved authorizations"
        )

    @mock.patch("requests.get")
    def test_get_balance(self, mock_get):
        mock_get.return_value = MockRequest(
            {
                "status": True,
                "message": "Balances retrieved",
                "data": [{"currency": "NGN", "balance": 123120000}],
            }
        )
        result = self.api.transfer_api.check_balance()
        self.assertEqual(result, [{"currency": "NGN", "balance": 1231200}])

    @mock.patch("requests.get")
    def test_get_banks(self, mock_get):
        response = [
            {
                "name": "Access Bank",
                "slug": "access-bank",
                "code": "044",
                "longcode": "044150149",
                "gateway": "emandate",
                "pay_with_bank": False,
                "active": True,
                "is_deleted": None,
                "country": "Nigeria",
                "currency": "NGN",
                "type": "nuban",
                "id": 1,
                "createdAt": "2016-07-14T10:04:29.000Z",
                "updatedAt": "2019-06-18T10:52:46.000Z",
            }
        ]
        mock_get.return_value = MockRequest(
            {"status": True, "message": "Banks retrieved", "data": response}
        )
        result = self.api.transfer_api.get_banks()
        self.assertEqual(result[2], response)
        bank_info = self.api.transfer_api.get_bank("Access Bank")
        assert bank_info == response[0]

