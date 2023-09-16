from MySQLConn.MySQLConn import MySQLConn
from datetime import datetime, timedelta

db = MySQLConn()


def is_qualified_for_reward(crowdin_user_id: int) -> bool:
    """
    Check if a user qualify for reward
    :param crowdin_user_id: Crowdin user id
    :return: True if qualified, False otherwise
    """
    sql = ("SELECT `next-date` FROM reward WHERE `crowdin-user-id` = '%s' ORDER BY `next-date` DESC LIMIT 1"
           % crowdin_user_id)
    result = db.fetch_one(sql)
    if result is None:
        return True
    else:
        next_date = result[0]
        if datetime.now() >= next_date:
            return True
        else:
            return False


def add_new_reward_record(crowdin_user_id: int, code: str, reward_amount: int) -> bool:
    """
    Add new reward record to database
    :param crowdin_user_id: Crowdin user id
    :param code: Reward code
    :param reward_amount: Reward amount
    :return: None
    """
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    next_date = (datetime.now() + timedelta(days=reward_amount)).strftime("%Y-%m-%dT%H:%M:%S")
    sql = ("INSERT INTO `reward` (`crowdin-user-id`, `code`, `assign-date`, `next-date`) " 
           "VALUES ('%s', '%s', '%s', '%s')" % (crowdin_user_id, code, current_time, next_date))
    result = db.execute(sql)
    if result == 0:
        raise ValueError("Failed to add new reward record")
    return True

