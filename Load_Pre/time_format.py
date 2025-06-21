from datetime import datetime, date
import re

def convert_twitter_time(time_str: str, output_format: str = "%Y-%m-%d") -> str:
    """
    将Twitter API的时间格式转换为标准格式
    
    Args:
        time_str: Twitter时间字符串，如 "Sun Jan 21 21:37:57 +0000 2018"
        output_format: 输出格式，默认为 "%Y-%m-%d" (年-月-日)
    
    Returns:
        转换后的时间字符串
    """
    try:
        # Twitter时间格式: "Sun Jan 21 21:37:57 +0000 2018"
        # 对应的格式字符串: "%a %b %d %H:%M:%S %z %Y"
        dt = datetime.strptime(time_str, "%a %b %d %H:%M:%S %z %Y")

        dt_utc = dt.utctimetuple()
        dt_utc_obj = datetime(*dt_utc[:6])
        return dt_utc_obj.strftime(output_format)
        
    except ValueError as e:
        print(f"时间格式转换失败: {e}")
        return ""

def compare_date(twitter_time: str, target_date: str) -> int:
    """
    比较Twitter时间与目标日期
    
    Args:
        twitter_time: Twitter时间格式字符串
        target_date: 目标日期，支持格式: "2017.06.19", "2017-06-19", "2017/06/19"
    
    Returns:
        -1: twitter_time < target_date
         0: twitter_time == target_date  
         1: twitter_time > target_date
        99: 转换失败
    """
    try:
        # 转换Twitter时间为日期
        twitter_date_str = convert_twitter_time(twitter_time)
        if not twitter_date_str:
            return 99
        
        # 转换为date对象进行比较
        twitter_date = datetime.strptime(twitter_date_str, "%Y-%m-%d").date()
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        if twitter_date < target_date_obj:
            return -1
        elif twitter_date == target_date_obj:
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"日期比较失败: {e}")
        return 99

def compare_by_date_range(twitter_time:str, start_date: str, end_date: str) -> bool:
    """
    根据日期范围筛选项目
    
    Args:
        tweet_time: str
        start_date: 开始日期 (如 "2017.06.01")
        end_date: 结束日期 (如 "2017.06.30")
    
    Returns:
        是否在日期范围内
    """
    start_compare = compare_date(twitter_time, start_date)
    end_compare = compare_date(twitter_time, end_date)
            
    # 在范围内：>= start_date 且 <= end_date
    if start_compare >= 0 and end_compare <= 0:
        return True
    
    return False

    
if __name__ == "__main__":
    time_ = "Sun Jan 21 21:37:57 +0000 2018"
    out = convert_twitter_time(time_)
    print(f"result of convert is {out}")
    is_inrange = compare_by_date_range(time_, "2018-01-18", "2018-01-20")
    print(f"filter check is {is_inrange}")