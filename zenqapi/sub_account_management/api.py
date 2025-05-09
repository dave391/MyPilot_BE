import datetime
import uuid

import requests
from .auth import ZagAuth

class ZagApiClient:
    def __init__(self, base_url: str, auth_token: str, api_key: str = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.api_key = api_key

    def generate_token(self) -> str:
        return ZagAuth.generate_bearer_token(self.auth_token)

    def create_sub_account(self, customerid: int, new_username: str) -> dict:
        url = f"{self.base_url}/API/Backend/CreateSubAccount.php?customerid={customerid}&newUsername={new_username}&apiKey={self.api_key}&access_token={self.generate_token()}"
        response = requests.get(url)
        return response.json()

    def delete_sub_account(self,main_account_id:int, sub_account_id: int) -> dict:
        url = f"{self.base_url}/API/V2/Backend/SubUsers.php?action=GET&user_id={main_account_id}&apiKey={self.api_key}&access_token={self.generate_token()}"
               # f"action=DELETE"
               # f"&userId={main_account_id}&subUserCommonId="
               # f"{sub_account_id}
        response = requests.get(url)
        return response.json()

    def get_sub_account_balances(self, user_id) -> dict:
        url = f"{self.base_url}/API/Backend/UserBalancesPortfolioAPI3.php?userId={user_id}&apiKey={self.api_key}&access_token={self.generate_token()}"
        response = requests.get(url)
        return response.json()

    def add_transaction(
        self,
        operation: str,
        amount: str,
        force_debit: int,
        reference_code: str,
        currency_symbol: str,
        target_gl_account: str,
        user_id: int,
        voucher_type: str,
    ) -> dict:
        url = f"{self.base_url}/API/Backend/AddTransaction.php"
        payload = {
            "operation": operation,
            "amount": amount,
            "force_debit": force_debit,
            "reference_code": reference_code,
            "currency_symbol": currency_symbol,
            "target_gl_account": target_gl_account,
            "user_id": user_id,
            "voucher_type": voucher_type,
            "apiKey": self.api_key,
            "access_token": self.generate_token(),
        }
        response = requests.post(url, params=payload)
        return response.json()

