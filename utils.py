def time_period(input_str):  
    # 检查输入格式  
    if not input_str.count('-') == 3:  
        return -2  
      
    date_parts = input_str.split('-')  
    if len(date_parts) != 4:  
        return -2  
      
    year, month, day, period = date_parts  
      
    if not (year.isdigit() and month.isdigit() and day.isdigit() and period.isdigit()):  
        return -2  
      
    if int(period) not in [0, 1]:  
        return -2  
      
    # 获取当前日期和时间  
    import datetime  
    today = datetime.date.today()  
    current_time = datetime.datetime.now().time()  
      
    # 解析输入的日期  
    input_date = datetime.date(int(year), int(month), int(day))  
      
    # 判断日期是否已过期  
    if input_date < today:  
        return -1  
      
    # 判断是上午还是下午  
    if int(period) == 0:  
        if current_time.hour < 12:  
            return 5 if input_date == today else 1 if input_date == today + datetime.timedelta(days=1) else 3  
        else:  
            return 6 if input_date == today else 2 if input_date == today + datetime.timedelta(days=1) else 4  
    else:  
        if current_time.hour < 12:  
            return 6 if input_date == today else 2 if input_date == today + datetime.timedelta(days=1) else 4  
        else:  
            return 5 if input_date == today else 1 if input_date == today + datetime.timedelta(days=1) else 3

# print(time_period("2023-12-12-0"))  # 输出 5，表示今天上午  
# print(time_period("2023-12-12-1"))  # 输出 6，表示今天下午  
# print(time_period("2023-12-13-0"))  # 输出 1，表示明天上午  
# print(time_period("2023-12-13-1"))  # 输出 2，表示明天下午  
# print(time_period("2023-12-14-0"))  # 输出 3，表示后天上午  
# print(time_period("2023-12-14-1"))  # 输出 4，表示后天下午  
# print(time_period("2023-12-11-0"))  # 输出 -1，表示已过期  
# print(time_period("2023-12-12-2"))  # 输出 -2，表示其他情况