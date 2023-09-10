from CrowdinClient import CrowdinClient
from config import TOKEN, PROJECT_ID, BRANCH_NAME, PROJECT_START_YEAR, PROJECT_START_MONTH, PROJECT_START_DAY, \
    REWARD_MESSAGE, IGNORED_MEMBERS, CODE_SYSTEM_KEY
from datetime import datetime, timedelta
from dateutil import tz
import httpx
import reward_history
import os
import schedule

client = CrowdinClient(TOKEN, PROJECT_ID, BRANCH_NAME,
                       datetime(PROJECT_START_YEAR, PROJECT_START_MONTH, PROJECT_START_DAY, tzinfo=tz.gettz("UTC")))


def generate_top_contributors_from_all_time_report():
    """
    Generate a list of all time top contributors
    From start date of project to current time
    Reward line is 6% of total project branch string count
    Reward line is 50% winning rate
    Reward for each contributor is 180 days
    :return: list of contributors, including username, user_id, user_full_name, translated_string
    """
    report = client.get_project_contributions(report_name="All Time Contributors Report")
    current_reward_line = client.get_total_project_branch_string_count() * 0.06
    contributors = [{"username": user["user"]["username"],
                     "user_id": user["user"]["id"],
                     "user_full_name": user["user"]["fullName"],
                     "translated_string": user["translated"],
                     "winning_string": user["winning"],
                     "reward": 180} for user in report["data"]
                    if user["translated"] >= current_reward_line
                    and user["winning"] / user["translated"] >= 0.5
                    and user["user"]["username"] not in IGNORED_MEMBERS]
    return contributors


def generate_top_contributors_for_previous_60_days():
    """
    Generate a list of top contributors for previous 67 days
    Ignore close 7 days, to avoid translate not been reviewed
    Reward line is 3% of total project branch string count
    Reward line is 80% winning rate
    Reward for each contributor is 90 days
    :return:
    """
    report = client.get_project_contributions(report_name="60 Days Contributors Report",
                                              start_time=datetime.now(tz=tz.gettz("UTC")) - timedelta(days=67),
                                              end_time=datetime.now(tz=tz.gettz("UTC")) - timedelta(days=7))
    current_reward_line = client.get_total_project_branch_string_count() * 0.03
    contributors = [{"username": user["user"]["username"],
                     "user_id": user["user"]["id"],
                     "user_full_name": user["user"]["fullName"],
                     "translated_string": user["translated"],
                     "winning_string": user["winning"],
                     "reward": 90} for user in report["data"]
                    if user["translated"] >= current_reward_line
                    and user["winning"] / user["translated"] >= 0.8
                    and user["user"]["username"] not in IGNORED_MEMBERS]
    return contributors


def get_all_rewarded_user():
    report = generate_top_contributors_from_all_time_report() + generate_top_contributors_for_previous_60_days()
    reward_dict = {}
    for user in report:
        user_id = user['user_id']
        reward = user['reward']
        user_name = user['user_full_name']

        if user_id in reward_dict:
            if reward <= reward_dict[user_id][0]:
                continue

        qualified = reward_history.is_qualified_for_reward(user_id)
        print(f"User {user_name} ({user_id}) qualification: {qualified}")
        if qualified:
            reward_dict[user_id] = [reward, user_name]
    return reward_dict


def main():
    print("Start running reward system: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    os.makedirs("./cache/", exist_ok=True)
    # Get all rewarded user
    reward_list = get_all_rewarded_user()
    # Generate reward code
    for k, v in reward_list.items():
        body = {
            "n": 1,
            "v": v[0],
            "desc": "Crowdin Reward for %s" % v[1]
        }
        header = {
            "Authorization": "X-API-KEY %s" % CODE_SYSTEM_KEY
        }
        request = httpx.post("https://homa.snapgenshin.com/code/management/add",
                             json=body, headers=header)
        if request.status_code != 200:
            msg = f"Failed to generate reward code for {v[1]} ({k})"
            client.send_system_message(msg)
        else:
            generated_code = request.content.decode("utf-8")
            result = reward_history.add_new_reward_record(k, generated_code, v[0])
            if result:
                user_notification_msg = REWARD_MESSAGE.format(user_full_name=v[1],
                                                              reward=v[0],
                                                              license_key=generated_code)
                print(user_notification_msg)
                client.send_project_member_message(k, user_notification_msg)
            if not result:
                msg = f"Failed to add reward record for {v[1]} ({k})"
                client.send_system_message(msg)
    print("End of reward system: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    schedule.every().day.at("10:00", "Asia/Shanghai").do(main)

    while True:
        schedule.run_pending()
