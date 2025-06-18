import ijson
import csv
import json
from datetime import datetime
import sys
from pathlib import Path

class TwitterProcessor:
    def __init__(self, input_file, output_file):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.processed_count = 0
        self.uk_tweets_count = 0
        self.output_feature = ['coordinates', 'text', 'created_at', 'user_location']
        
    def process_stream(self):
        print(f"开始处理文件: {self.input_file}")
        print(f"输出文件: {self.output_file}")
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.input_file, 'rb') as input_f, \
                 open(self.output_file, 'w', newline='', encoding='utf-8') as output_f:
                
                csv_writer = csv.writer(output_f)
                csv_writer.writerow(self.output_feature)
                
                try:
                    parser = ijson.items(input_f, 'item')
                except:
                    # 如果不是数组，重新打开文件按行处理
                    input_f.seek(0)
                    parser = self._parse_jsonl(input_f)
                
                for tweet in parser:
                    self.processed_count += 1
                    
                    if self.processed_count % 10000 == 0:
                        print(f"已处理: {self.processed_count:,} 条记录, 英国推文: {self.uk_tweets_count:,} 条")
                    
                    # 检查是否为英国推文
                    if self._is_uk_tweet(tweet):
                        self.uk_tweets_count += 1
                        self._write_tweet_to_csv(tweet, csv_writer)
                        
        except FileNotFoundError:
            print(f"错误: 找不到输入文件 {self.input_file}")
            return False
        except Exception as e:
            print(f"处理过程中发生错误: {e}")
            return False
            
        print(f"\n处理完成!")
        print(f"总处理记录: {self.processed_count:,}")
        print(f"英国推文数量: {self.uk_tweets_count:,}")
        print(f"筛选率: {(self.uk_tweets_count/self.processed_count)*100:.2f}%")
        
        return True
    
    def _parse_jsonl(self, file_obj):
        """解析JSONL格式（每行一个JSON对象）"""
        for line in file_obj:
            line = line.decode('utf-8').strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    
    def _is_uk_tweet(self, tweet):
        """判断是否为英国推文"""
        # 方法1: 检查place字段的country_code
        place = tweet.get('place')
        if place and place.get('country_code') == 'UK':
            return True
            
        # 方法2: 检查user的location信息（备用）
        user = tweet.get('user', {})
        location = user.get('location', '').upper()
        uk_keywords = ['UK', 'UNITED KINGDOM', 'ENGLAND', 'SCOTLAND', 'WALES', 'NORTHERN IRELAND', 'BRITAIN']
        
        return any(keyword in location for keyword in uk_keywords)
    
    def _write_tweet_to_csv(self, tweet, csv_writer):
        """将推文数据写入CSV"""
        coordinates = self._extract_coordinates(tweet)
        text = tweet.get('text', '').replace('\n', ' ').replace('\r', ' ')

        created_at = tweet.get('created_at', '')
        user_location = tweet.get('user', {}).get('location', '')
        
        # 写入CSV行
        csv_writer.writerow([coordinates, text, created_at, user_location])
    
    def _extract_coordinates(self, tweet):
        """提取坐标信息"""
        # 检查coordinates字段
        coordinates = tweet.get('coordinates')
        if coordinates and coordinates.get('coordinates'):
            coords = coordinates['coordinates']
            return f"{coords[1]},{coords[0]}"  # lat,lng格式
        
        # 检查geo字段
        geo = tweet.get('geo')
        if geo and geo.get('coordinates'):
            coords = geo['coordinates']
            return f"{coords[0]},{coords[1]}"  # lat,lng格式
            
        # 检查place的bounding_box
        place = tweet.get('place')
        if place and place.get('bounding_box'):
            bbox = place['bounding_box'].get('coordinates', [[]])[0]
            if bbox:
                # 计算边界框中心点
                lngs = [coord[0] for coord in bbox]
                lats = [coord[1] for coord in bbox]
                center_lng = sum(lngs) / len(lngs)
                center_lat = sum(lats) / len(lats)
                return f"{center_lat},{center_lng}"
        
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