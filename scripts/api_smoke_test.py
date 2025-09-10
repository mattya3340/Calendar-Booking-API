"""
Standalone API smoke test script for Calendar Booking API.

Usage:
  python scripts/api_smoke_test.py --base-url http://127.0.0.1:8000/api/v1

Notes:
- Authentication is disabled in this project; all endpoints are public.
- The script creates temporary data (user, business hours, weekly-holiday rule, events) and validates core flows.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import string
import sys
from typing import Any, Dict, Optional

import requests


class APITester:
    def __init__(self, base_url: str, verbose: bool = True):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.created_event_ids = []
        self.created_user_ids = []
        self.created_weekly_rule_ids = []
        self.created_holiday_ids = []

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _print(self, title: str, payload: Optional[Dict[str, Any]] = None):
        if not self.verbose:
            return
        print(f"\n=== {title} ===")
        if payload is not None:
            print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))

    def _expect(self, resp: requests.Response, expected_status: int | list[int]):
        exp_list = expected_status if isinstance(expected_status, list) else [expected_status]
        if resp.status_code not in exp_list:
            raise AssertionError(
                f"Expected {exp_list} but got {resp.status_code}: {resp.text}"
            )

    # -------- Users --------
    def test_users(self):
        # List users
        r = requests.get(self._url("/users"))
        self._print("GET /users", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)

        # Create user
        rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        email = f"test_{rand}@example.com"
        payload = {
            "email": email,
            "password": "Passw0rd!",
            "full_name": "Test User",
            "phone_number": "090-0000-0000",
            "is_active": True,
            "is_superuser": False
        }
        r = requests.post(self._url("/users"), json=payload)
        self._print("POST /users", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)
        user = r.json()
        self.created_user_ids.append(user["id"])  # response_model=User

    # -------- Business Hours --------
    def test_business_hours(self):
        # Upsert business hours for Tuesday (1): 09:00-18:00
        payload = {"weekday": 1, "open_time": "09:00:00", "close_time": "18:00:00"}
        r = requests.put(self._url("/business-hours/1"), json=payload)
        self._print("PUT /business-hours/1", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)

        # List business hours
        r = requests.get(self._url("/business-hours"))
        self._print("GET /business-hours", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)

    # -------- Weekly Holidays --------
    def test_weekly_holidays(self):
        # Add weekly holiday rule for Wednesday (2)
        payload = {"weekday": 2, "name": "毎週水曜 定休"}
        r = requests.post(self._url("/weekly-holidays"), json=payload)
        self._print("POST /weekly-holidays", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)
        rule = r.json()
        self.created_weekly_rule_ids.append(rule["id"])  # for cleanup/deactivation if needed

        # Get occurrences for next 14 days
        start = dt.date.today()
        end = start + dt.timedelta(days=14)
        r = requests.get(self._url("/weekly-holidays/occurrences"), params={
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        })
        self._print("GET /weekly-holidays/occurrences", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)

    # -------- Holidays (one-off) --------
    def test_holidays(self):
        # Create a one-off holiday for today + 1 day
        target_day = dt.date.today() + dt.timedelta(days=1)
        payload = {
            "event_date": target_day.isoformat(),
            "start_time": "00:00:00",
            "end_time": "23:59:00",
            "representative_name": "System",
            "phone_number": "000",
            "is_holiday": True,
            "holiday_name": "臨時休業",
        }
        r = requests.post(self._url("/holidays"), json=payload)
        self._print("POST /holidays", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)
        hol = r.json()
        self.created_holiday_ids.append(hol["id"])  # can be deleted later

        # List holidays in range
        r = requests.get(self._url("/holidays"), params={
            "start_date": target_day.isoformat(),
            "end_date": (target_day + dt.timedelta(days=1)).isoformat(),
        })
        self._print("GET /holidays", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)

    # -------- Events (booking) --------
    def test_events(self):
        today = dt.date.today()
        # Choose a non-holiday weekday: Thursday (3) assuming Wed is weekly holiday
        # Find next Thursday
        offset = (3 - today.weekday() + 7) % 7 + 7 # Find next Thursday and add 7 days
        day = today + dt.timedelta(days=offset)

        # Create an event inside business hours (Tue is configured; but we use Thu with no BH -> should pass unless BH set)
        # To ensure BH validation, also set BH for Thursday (3): 09:00-18:00
        requests.put(self._url("/business-hours/3"), json={"weekday": 3, "open_time": "09:00:00", "close_time": "18:00:00"})

        payload_ok = {
            "event_date": day.isoformat(),
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "representative_name": "予約 太郎",
            "phone_number": "090-1111-2222",
            "num_adults": 2,
            "num_children": 0
        }
        r = requests.post(self._url("/events"), json=payload_ok)
        self._print("POST /events (ok)", r.json() if r.headers.get("content-type", "").startswith("application/json") else {"text": r.text})
        self._expect(r, 200)
        ev = r.json()
        self.created_event_ids.append(ev["id"])  # for cleanup

        # Try overlapping event -> expect 409
        payload_overlap = {
            **payload_ok,
            "start_time": "10:30:00",
            "end_time": "11:30:00",
        }
        r = requests.post(self._url("/events"), json=payload_overlap)
        self._print("POST /events (overlap)", {"status": r.status_code, "text": r.text})
        self._expect(r, 409)

        # Try outside business hours -> expect 409
        payload_oob = {
            **payload_ok,
            "start_time": "08:00:00",
            "end_time": "08:30:00",
        }
        r = requests.post(self._url("/events"), json=payload_oob)
        self._print("POST /events (outside BH)", {"status": r.status_code, "text": r.text})
        self._expect(r, 409)

    # -------- Cleanup --------
    def cleanup(self):
        # Delete created events
        for eid in self.created_event_ids:
            try:
                r = requests.delete(self._url(f"/events/{eid}"))
                self._print(f"DELETE /events/{eid}", {"status": r.status_code, "text": r.text})
            except Exception as e:
                self._print(f"DELETE /events/{eid} failed", {"error": str(e)})
        # Delete created holiday
        for hid in self.created_holiday_ids:
            try:
                r = requests.delete(self._url(f"/holidays/{hid}"))
                self._print(f"DELETE /holidays/{hid}", {"status": r.status_code, "text": r.text})
            except Exception as e:
                self._print(f"DELETE /holidays/{hid} failed", {"error": str(e)})
        # Deactivate weekly holiday rules
        for rid in self.created_weekly_rule_ids:
            try:
                r = requests.delete(self._url(f"/weekly-holidays/{rid}"))
                self._print(f"DELETE /weekly-holidays/{rid}", {"status": r.status_code, "text": r.text})
            except Exception as e:
                self._print(f"DELETE /weekly-holidays/{rid} failed", {"error": str(e)})
        
        # Delete created users
        for uid in self.created_user_ids:
            try:
                r = requests.delete(self._url(f"/users/{uid}"))
                self._print(f"DELETE /users/{uid}", {"status": r.status_code, "text": r.text})
            except Exception as e:
                self._print(f"DELETE /users/{uid} failed", {"error": str(e)})



    def cleanup_all_test_data(self):
        """
        より強力なクリーンアップ処理。
        現在の実行だけでなく、過去のテストで残ってしまった可能性のある
        すべてのテストデータをAPI経由で検索し、削除する。
        """
        self._print("Running aggressive pre-test cleanup...", {})
        
        # イベントをクリーンアップ
        try:
            r = requests.get(self._url("/events"), params={"limit": 500})
            if r.status_code == 200:
                for event in r.json():
                    if event.get("representative_name") == "予約 太郎":
                        requests.delete(self._url(f"/events/{event['id']}"))
        except Exception:
            pass # エラーが出ても続行

        # ユーザーをクリーンアップ (superuserは除く)
        try:
            r = requests.get(self._url("/users"), params={"limit": 500})
            if r.status_code == 200:
                for user in r.json():
                    if user.get("email", "").startswith("test_") and not user.get("is_superuser"):
                        requests.delete(self._url(f"/users/{user['id']}"))
        except Exception:
            pass

        # 定休日ルールをクリーンアップ
        try:
            r = requests.get(self._url("/weekly-holidays"))
            if r.status_code == 200:
                for rule in r.json():
                    if rule.get("name") == "毎週水曜 定休":
                        requests.delete(self._url(f"/weekly-holidays/{rule['id']}"))
        except Exception:
            pass

        # 祝日をクリーンアップ
        try:
            start = dt.date.today() - dt.timedelta(days=7)
            end = start + dt.timedelta(days=30)
            r = requests.get(self._url("/holidays"), params={"start_date": start.isoformat(), "end_date": end.isoformat()})
            if r.status_code == 200:
                for holiday in r.json():
                    if holiday.get("holiday_name") == "臨時休業":
                        requests.delete(self._url(f"/holidays/{holiday['id']}"))
        except Exception:
            pass

    def run(self):
        try:
            self._print("Base URL", {"base_url": self.base_url})
            
            # Clean up any leftover data from previous failed runs before starting
            self._print("Pre-test cleanup", {})
            self.cleanup_all_test_data()

            self.created_event_ids = []
            self.created_user_ids = []
            self.created_weekly_rule_ids = []
            self.created_holiday_ids = []
            
            self.test_users()
            self.test_business_hours()
            self.test_weekly_holidays()
            self.test_holidays()
            self.test_events()
            self._print("All tests finished successfully ✅")
        except Exception as e:
            self._print("Test failed ❌", {"error": str(e)})
            raise
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api/v1", help="Base URL of the API (default: http://127.0.0.1:8000/api/v1)")
    parser.add_argument("--quiet", action="store_true", help="Reduce output")
    args = parser.parse_args()

    tester = APITester(base_url=args.base_url, verbose=not args.quiet)
    tester.run()


if __name__ == "__main__":
    main()
