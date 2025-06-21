import json
import os
from typing import Optional


def find_last_created_at(file_path: str, chunk_size: int = 8192) -> Optional[str]:
    """
    从超大JSON文件中找到最后一个项目的created_at属性

    Args:
        file_path: JSON文件路径
        chunk_size: 每次读取的字节数

    Returns:
        最后一个项目的created_at值，如果未找到则返回None
    """

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as f:
        # 从文件末尾开始向前搜索
        buffer = b""
        last_created_at = None
        brace_count = 0
        in_string = False
        escape_next = False

        # 从文件末尾开始读取
        pos = file_size

        while pos > 0:
            # 计算本次读取的位置和大小
            read_size = min(chunk_size, pos)
            pos -= read_size

            # 移动到读取位置
            f.seek(pos)
            chunk = f.read(read_size)

            # 将新读取的内容添加到缓冲区前面
            buffer = chunk + buffer

            # 从右到左解析JSON结构
            try:
                # 尝试找到完整的JSON对象
                reversed_buffer = buffer[::-1]  # 反转字节序列

                # 寻找最后一个完整的JSON对象
                json_str = buffer.decode("utf-8", errors="ignore")

                # 使用简单的状态机找到最后一个对象
                last_obj_start = -1
                brace_count = 0

                for i in range(len(json_str) - 1, -1, -1):
                    char = json_str[i]

                    if char == "}" and not in_string:
                        brace_count += 1
                    elif char == "{" and not in_string:
                        brace_count -= 1
                        if brace_count == 0:
                            last_obj_start = i
                            break
                    elif char == '"' and not escape_next:
                        in_string = not in_string

                    escape_next = char == "\\" and not escape_next

                if last_obj_start >= 0:
                    # 找到最后一个对象，尝试解析
                    last_obj_str = json_str[last_obj_start:]

                    # 找到对象的结束位置
                    brace_count = 0
                    in_string = False
                    escape_next = False
                    obj_end = -1

                    for i, char in enumerate(last_obj_str):
                        if char == "{" and not in_string:
                            brace_count += 1
                        elif char == "}" and not in_string:
                            brace_count -= 1
                            if brace_count == 0:
                                obj_end = i + 1
                                break
                        elif char == '"' and not escape_next:
                            in_string = not in_string

                        escape_next = char == "\\" and not escape_next

                    if obj_end > 0:
                        try:
                            obj_json = last_obj_str[:obj_end]
                            obj_data = json.loads(obj_json)

                            if isinstance(obj_data, dict) and "created_at" in obj_data:
                                return obj_data["created_at"]
                        except json.JSONDecodeError:
                            pass

            except UnicodeDecodeError:
                continue

            # 如果已经读取了足够多的内容但没找到，继续读取
            if len(buffer) > chunk_size * 10:  # 限制缓冲区大小
                buffer = buffer[-chunk_size * 5 :]  # 保留后半部分

    return None


def find_last_created_at_alternative(file_path: str) -> Optional[str]:
    """
    替代方案：使用ijson流式解析（需要安装ijson库）
    pip install ijson
    """
    try:
        import ijson

        last_created_at = None

        with open(file_path, "rb") as f:
            # 假设JSON文件是一个数组格式
            parser = ijson.parse(f)
            current_item = {}
            in_item = False

            for prefix, event, value in parser:
                if event == "start_map":
                    current_item = {}
                    in_item = True
                elif event == "end_map" and in_item:
                    if "created_at" in current_item:
                        last_created_at = current_item["created_at"]
                    in_item = False
                elif event == "string" and prefix.endswith(".created_at"):
                    current_item["created_at"] = value

        return last_created_at

    except ImportError:
        print("ijson库未安装，请使用: pip install ijson")
        return None


def find_last_items(
    file_path: str, num_items: int = 20, chunk_size: int = 8192
) -> list:
    """
    从超大JSON文件中找到最后N个项目

    Args:
        file_path: JSON文件路径
        num_items: 要获取的项目数量
        chunk_size: 每次读取的字节数

    Returns:
        最后N个项目的列表
    """

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as f:
        # 从文件末尾开始向前搜索
        buffer = b""
        found_items = []

        # 从文件末尾开始读取
        pos = file_size

        while pos > 0 and len(found_items) < num_items:
            # 计算本次读取的位置和大小
            read_size = min(chunk_size, pos)
            pos -= read_size

            # 移动到读取位置
            f.seek(pos)
            chunk = f.read(read_size)

            # 将新读取的内容添加到缓冲区前面
            buffer = chunk + buffer

            try:
                json_str = buffer.decode("utf-8", errors="ignore")

                # 从右到左找到所有完整的JSON对象
                items_in_buffer = []
                i = len(json_str) - 1

                while i >= 0 and len(found_items) + len(items_in_buffer) < num_items:
                    # 寻找对象结束符
                    if json_str[i] == "}":
                        obj_end = i + 1
                        brace_count = 1
                        in_string = False
                        escape_next = False

                        # 向前找到对象开始符
                        j = i - 1
                        while j >= 0 and brace_count > 0:
                            char = json_str[j]

                            if char == '"' and not escape_next:
                                in_string = not in_string
                            elif not in_string:
                                if char == "}":
                                    brace_count += 1
                                elif char == "{":
                                    brace_count -= 1

                            escape_next = char == "\\" and not escape_next
                            j -= 1

                        if brace_count == 0:
                            obj_start = j + 1
                            try:
                                obj_json = json_str[obj_start:obj_end]
                                obj_data = json.loads(obj_json)
                                if isinstance(obj_data, dict):
                                    items_in_buffer.append(obj_data)
                                i = obj_start - 1
                            except json.JSONDecodeError:
                                i -= 1
                        else:
                            i -= 1
                    else:
                        i -= 1

                # 将找到的项目添加到结果中（注意顺序）
                found_items = items_in_buffer + found_items

            except UnicodeDecodeError:
                continue

            # 限制缓冲区大小，防止内存溢出
            if len(buffer) > chunk_size * 20:
                # 保留后半部分，确保不会截断JSON对象
                buffer = buffer[-chunk_size * 10 :]

    return found_items[-num_items:] if found_items else []


def print_items_info(items: list, show_full: bool = False):
    """
    打印项目信息的辅助函数

    Args:
        items: 项目列表
        show_full: 是否显示完整信息
    """
    if not items:
        print("未找到任何项目")
        return

    print(f"找到 {len(items)} 个项目:")
    print("=" * 50)

    for i, item in enumerate(items, 1):
        print(f"\n项目 {i}:")

        if show_full:
            # 显示完整信息
            for key, value in item.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        else:
            # 只显示关键字段
            key_fields = ["id", "created_at", "updated_at", "name", "title", "status"]
            for field in key_fields:
                if field in item:
                    print(f"  {field}: {item[field]}")

            # 显示其他字段名
            other_fields = [k for k in item.keys() if k not in key_fields]
            if other_fields:
                print(f"  其他字段: {', '.join(other_fields)}")

    print("=" * 50)


# 使用示例
if __name__ == "__main__":
    file_path = "/media/ys_tum/T7 Shield/tweets_europe_west_2017_05_17.json"

    print("使用自定义解析器读取最后20个项目...")
    items = find_last_items(file_path, num_items=20)
    print_items_info(items)
    """
    # 方法1：自定义解析器
    print("使用自定义解析器...")
    result = find_last_created_at(file_path)
    if result:
        print(f"")
    else:
        print("未找到created_at字段")
    """

    """
    # 方法2：使用ijson库（推荐）
    print("\n使用ijson库...")
    result_alt = find_last_created_at_alternative(file_path)
    if result_alt:
        print(f"最后一个项目的created_at: {result_alt}")
    else:
        print("未找到created_at字段或ijson库未安装")
    """
