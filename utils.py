from datetime import datetime
  
def parse_date_string(date_str):  
    try:  
        # 解析日期字符串  
        date_parts = date_str.split('-')  
        year, month, day, x = map(int, date_parts)  
        current_date = datetime.now().date()  
        input_date = datetime(year, month, day).date()  
          
        # 检查日期是否已过期  
        if input_date < current_date:  
            return -1  
          
        # 根据x的值判断上午还是下午  
        if x == 0:  
            if input_date == current_date:  
                return 1  
            else:  
                return 3  
        elif x == 1:  
            if input_date == current_date:  
                return 2  
            else:  
                return 4  
        else:  
            return -2  
    except ValueError:  
        return -2  

if __name__ == "__main__":
    # 测试函数  
    print(parse_date_string("2023-12-12-0"))  # 今天上午，应返回1  
    print(parse_date_string("2023-12-12-1"))  # 今天下午，应返回2  
    print(parse_date_string("2023-12-13-0"))  # 明天上午，应返回3  
    print(parse_date_string("2023-12-13-1"))  # 明天下午，应返回4  
    print(parse_date_string("2023-12-11-0"))  # 已过期，应返回-1  
    print(parse_date_string("2023-12-12-2"))  # 其他，应返回-2