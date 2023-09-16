import httpx
from datetime import datetime, timedelta
from dateutil import tz

COMMUNITY_MEMBER_ROLES = ["proofreader", "translator"]


class CrowdinClient:
    def __init__(self, api_token, project_id, branch_name: str, project_start_date: datetime):
        self.__api_token = api_token
        self.project_id = project_id
        self.host = "https://api.crowdin.com/api/v2"
        self.__headers = {"Authorization": f"Bearer {api_token}"}
        self.project_start_date = project_start_date
        self.branch_id = None

        response = httpx.get(f"{self.host}/projects/{self.project_id}/branches", headers=self.__headers)
        for branch in response.json()["data"]:
            if branch["data"]["name"] == branch_name:
                self.branch_id = branch["data"]["id"]
                break
        if self.branch_id is None:
            raise ValueError(f"Branch {branch_name} not found")

    def get_project_community_members_info(self):
        endpoint = f"{self.host}/projects/{self.project_id}/members"
        response = httpx.get(endpoint, headers=self.__headers,
                             params={"limit": 500, "role": COMMUNITY_MEMBER_ROLES})
        if response.status_code != 200:
            raise ValueError(f"HTTP Error: {response.status_code}")
        return response.json()

    def get_project_contributions(self, report_name: str, start_time: datetime = None, end_time: datetime = None):
        """
        Generate a report of all time top contributors
        :param report_name: Report file name, used for cache file naming
        :param start_time: Start time of the report, default to project start date
        :param end_time: End time of the report, default to current time
        :return: Report body
        """
        if start_time is None:
            start_time = self.project_start_date.isoformat()
        else:
            start_time = start_time.isoformat()

        if end_time is None:
            end_time = datetime.now(tz=tz.gettz("UTC")).isoformat()
        else:
            end_time = end_time.isoformat()

        # Request to generate the report
        endpoint = f"{self.host}/projects/{self.project_id}/reports"
        body = {
            "name": "top-members",
            "schema": {
                "unit": "strings",
                "format": "json",
                "dateFrom": start_time,
                "dateTo": end_time
            }
        }
        response = httpx.post(endpoint, headers=self.__headers, json=body)
        if response.status_code != 201:
            raise ValueError(f"HTTP Error: {response.status_code}\n"
                             f"Message: {response.json()}")
        report_id = response.json()["data"]["identifier"]
        while True:
            # Wait for the report to be generated
            endpoint = f"{self.host}/projects/{self.project_id}/reports/{report_id}"
            response = httpx.get(endpoint, headers=self.__headers)
            try:
                if response.json()["data"]["status"] == "finished":
                    break
            except KeyError:
                pass
        # Get the report download URL
        endpoint = f"{self.host}/projects/{self.project_id}/reports/{report_id}/download"
        response = httpx.get(endpoint, headers=self.__headers)
        report_url = response.json()["data"]["url"]
        # Download the report
        response = httpx.get(report_url)
        with open(f"./cache/{datetime.now().strftime('%Y%m%d%H%M%S')} - {report_name}.json", "wb") as f:
            f.write(response.content)
        return response.json()

    def get_total_project_word_count_by_string(self):
        endpoint = f"{self.host}/projects/{self.project_id}/strings"
        offset = 0
        while True:
            response = httpx.get(endpoint, headers=self.__headers, params={"limit": 500, "offset": offset})
            if response.status_code != 200:
                raise ValueError(f"HTTP Error: {response.status_code}")
            if len(response.json()["data"]) == 500:
                offset += 500
            if len(response.json()["data"]) < 500:
                offset += len(response.json()["data"])
                break
        return offset

    def get_total_project_branch_string_count(self):
        endpoint = f"{self.host}/projects/{self.project_id}/branches/{self.branch_id}/languages/progress"
        response = httpx.get(endpoint, headers=self.__headers)
        if response.status_code != 200:
            raise ValueError(f"HTTP Error: {response.status_code}")
        return response.json()["data"][0]["data"]["phrases"]["total"]

    def send_system_message(self, msg: str):
        endpoint = f"{self.host}/notify"
        body = {
            "message": msg
        }
        response = httpx.post(endpoint, headers=self.__headers, json=body)
        if response.status_code != 204:
            raise ValueError(f"HTTP Error: {response.status_code}\n"
                             f"Message: {response.json()}")
        return True

    def send_project_member_message(self, msg: str, user_ids: list | int):
        endpoint = f"{self.host}/projects/{self.project_id}/notify"
        body = {
            "message": msg,
            "userIds": user_ids if type(user_ids) is list else [int(user_ids)]
        }
        response = httpx.post(endpoint, headers=self.__headers, json=body)
        if response.status_code != 204:
            raise ValueError(f"HTTP Error: {response.status_code}\n"
                             f"Message: {response.json()}")
        return True
