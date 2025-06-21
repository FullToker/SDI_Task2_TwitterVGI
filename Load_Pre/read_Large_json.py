import ijson
import csv
import json
from datetime import datetime
import sys
from pathlib import Path
from time_format import compare_date, compare_by_date_range

month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
num_month_map = {value: key for key, value in month_map.items()}

"""
运行前注意： 
1、coordinates的不同feature
2、预估时间以计算跳过的推文数量,一天约70万条推文
3、更改时间range或者地点
4、检查需要记录的feature

"""


class TwitterProcessor:
    def __init__(
        self,
        input_file,
        output_file,
        feature=["coordinates", "location", "text", "created_at", "lang", "hashTags"],
    ):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.processed_count = 0
        self.uk_tweets_count = 0
        self.output_feature = feature

    def process_stream(self):
        print(f"开始处理文件: {self.input_file}")
        print(f"输出文件: {self.output_file}")

        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.input_file, "rb") as input_f, open(
                self.output_file, "w", newline="", encoding="utf-8"
            ) as output_f:

                csv_writer = csv.writer(output_f)
                csv_writer.writerow(self.output_feature)

                try:
                    parser = ijson.items(input_f, "item")
                except:
                    input_f.seek(0)
                    parser = self._parse_jsonl(input_f)

                for tweet in parser:
                    self.processed_count += 1
                    '''
                    if self.processed_count <= 7:
                        print(tweet)'''
                    # if self.processed_count == 1:
                    #    print(tweet['country_code'])
                    if self. processed_count<20000000:
                        continue
                    if self.processed_count % 10000000 == 0:
                        print(
                            f"已处理: {self.processed_count:,} 条记录, 符合条件的推文: {self.uk_tweets_count:,} 条"
                        )

                    """检查是否符合初始条件（时间 地点等）"""
                    if self._is_time_tweet(tweet):
                        self.uk_tweets_count += 1
                        self._write_tweet_to_csv(tweet, csv_writer)


        except FileNotFoundError:
            print(f"错误: 找不到输入文件 {self.input_file}")
            return False
        except Exception as e:
            print(f"处理过程中发生错误: {e}")
            print(f"错误详情:")
            return False

        print(f"\n处理完成!")
        print(f"总处理记录: {self.processed_count:,}")
        print(f"时间范围内推文数量: {self.uk_tweets_count:,}")
        print(f"筛选率: {(self.uk_tweets_count/self.processed_count)*100:.2f}%")

        return True

    def _parse_jsonl(self, file_obj):
        """解析JSONL格式（每行一个JSON对象）"""
        for line in file_obj:
            line = line.decode("utf-8").strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def _is_uk_tweet(self, tweet):
        """判断是否为英国推文"""
        # 方法1: 检查place字段的country_code
        if tweet.get("country_code", "") == "GB":
            return True

        # 方法2: 检查user的location信息（备用）
        location = tweet.get("country", "").upper()
        uk_keywords = [
            "UK",
            "UNITED KINGDOM",
            "ENGLAND",
            "SCOTLAND",
            "WALES",
            "NORTHERN IRELAND",
            "BRITAIN",
        ]

        return any(keyword in location for keyword in uk_keywords)
    
    def _is_time_tweet(self, tweet, filtered_time = ["2017-06-19", "2017-06-20"]) -> bool:
        """check if the tweet created at the time range
            time_str:  Sun Jan 21 21:37:56 +0000 2018
        """
        time_str = tweet.get("created_at","")
        # corse filter
        if time_str == "":
            return False
        # print(f"月份为:{time_str[4:7]}.")
        if time_str[4:7] != num_month_map[int(filtered_time[0][5:7])]:
            return False

        if compare_date(time_str, filtered_time[0]) ==-1:
            return False
        if compare_date(time_str, filtered_time[1]) ==1:
            return False
        if compare_by_date_range(time_str, filtered_time[0], filtered_time[1]):
            return True
        
        return False
        

    def _write_tweet_to_csv(self, tweet, csv_writer):
        """将推文数据写入CSV"""
        coordinates = self._extract_coordinates(tweet)
        location = tweet.get("location","")
        created_at = tweet.get("created_at", "")
        lang = tweet.get("lang", "")
        text = tweet.get("text", "").replace("\n", " ").replace("\r", " ")
        """
        if lang != "en":
            result = self.translator.translate(text, dest="en")
            text = result.text
        """
        hashtags = self._extract_hashtags_text(tweet)

        # 写入CSV行
        csv_writer.writerow([coordinates, location, text, created_at, lang, hashtags])

    def _extract_hashtags_text(self, tweet):
        raw = tweet.get("hashtags", "")
        if not raw:
            return ""
        if isinstance(raw, str):
            try:
                tags = json.loads(raw)
            except json.JSONDecodeError:
                return ""  # 解析失败也返回空串
        elif isinstance(raw, list):
            tags = raw
        else:
            return ""

        texts = [t.get("text", "").strip() for t in tags if t.get("text", "").strip()]
        if not texts:
            return ""
        return " ".join(texts)

    def _extract_coordinates(self, tweet):
        """提取坐标信息"""
        coordinates = tweet.get("coordinates")
        if coordinates:
            if isinstance(coordinates, str):
                # 如果是字符串格式，需要解析
                try:
                    coords = json.loads(coordinates)
                    if isinstance(coords, list) and len(coords) >= 2:
                        return f"{coords[1]},{coords[0]}"  # lat,lng格式
                except (json.JSONDecodeError, IndexError):
                    pass
            elif isinstance(coordinates, dict) and coordinates.get("coordinates"):
                # 如果是字典格式
                coords = coordinates["coordinates"]
                if isinstance(coords, list) and len(coords) >= 2:
                    return f"{coords[1]},{coords[0]}"  # lat,lng格式
        geo = tweet.get("geo")
        if geo and isinstance(geo, dict):
            coords = geo.get("coordinates")
            if isinstance(coords, list) and len(coords) >= 2:
                # geo字段中坐标通常是[lat, lng]格式，不需要交换顺序
                return f"{coords[0]},{coords[1]}"
    
        return ""  # 无坐标信息
        


def main():
    if len(sys.argv) != 3:
        print("用法: python twitter_processor.py <输入JSON文件> <输出CSV文件>")
        print("示例: python twitter_processor.py twitter_data.json uk_tweets.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # 检查输入文件是否存在
    if not Path(input_file).exists():
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)

    processor = TwitterProcessor(input_file, output_file)
    success = processor.process_stream()

    if success:
        print(f"数据已成功导出到: {output_file}")
    else:
        print("处理失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
