#########################################################################
# create on 2023-11-29
# @author: Violeta, email: violet2021@foxmail.com
# brief: a hospital appointment server through handling OM IVR menu
# Note: shutdown your firewall before you activate this script

#########################################################################
# custom config here

OM_IP = "10.16.18.150"  # your OM device's ip
HOST_ADDR = ("10.230.32.134", 8989) # your machine's ip and port
AMOUNT_LIMIT = 100  # register amount limit 每个 科室-门诊级别-时间段 挂号的数量限额
HUMAN_SERVE_PHONE_NUMBER = '5900'

#########################################################################
# Don't modify the following content 
# unless you do understand what will happen

import sqlite3
import OM_API, DB_API
from utils import *
from http.server import HTTPServer, SimpleHTTPRequestHandler
from http.client import HTTPConnection
from xml.dom import minidom

department_map = {
    '1':OM_API.waike,
    '2':OM_API.neike,
    '3':OM_API.erke,
    '4':OM_API.wuguanke,
    '5':OM_API.pifuke
}

level_voice_map = {
    '1': OM_API.putong,
    '2': OM_API.zhuanjia
}

http_client = HTTPConnection(OM_IP)
db_connect = sqlite3.connect("registers.db")
db_cusor = db_connect.cursor()
visitor_menu = {}
visitor_data = {}

def bussiness_process(visitor_id:str, info:str) -> None:
    menu = visitor_menu[visitor_id]
    voice_cmd = OM_API.OM_createVoiceCmd()

    '''
    特殊按键处理
    '''
    if info == '*':     # 返回上一级菜单
        menu = menu[:-1] if menu != '1' else menu
        visitor_menu[visitor_id] = menu
        OM_API.OM_menuPlay(http_client, visitor_id, menu)
        return
    elif info == '0':   # 重复当前菜单
        OM_API.OM_menuPlay(http_client, visitor_id, menu)
        return
    elif info == '8':
        visitor_menu[visitor_id] = '1'
        OM_API.OM_menuPlay(http_client, visitor_id, visitor_menu[visitor_id])
        return
    elif info == '9':   # 人工服务
        OM_API.OM_transferPhone(http_client, visitor_id, HUMAN_SERVE_PHONE_NUMBER)
        return
    elif info == 'T':   # 超时无按键输入挂断
        return


    '''
    语音菜单处理逻辑
    '''
    if menu == '1':     # 挂号还是取消挂号
        if info not in ['1', '2']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_menu[visitor_id] += info
            OM_API.OM_menuPlay(http_client, visitor_id, visitor_menu[visitor_id])

    elif menu == '11':  # 选择科室
        if info not in ['1', '2', '3', '4', '5']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['department'] = info
            visitor_menu[visitor_id] += '1'
            OM_API.OM_menuPlay(http_client, visitor_id, visitor_menu[visitor_id])

    elif menu == '111':  # 选择普通 or 专家门诊
        if info not in ['1', '2']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['level'] = info
            visitor_menu[visitor_id] += '1'
            OM_API.OM_menuPlay(http_client, visitor_id, visitor_menu[visitor_id])
    
    elif menu == '1111':  # 选择时间段
        if info not in ['1', '2', '3', '4', '5', '6']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:   # 下一级菜单
            today_date = ''
            tomarrow_date = ''
            visitor_data[visitor_id]['time'] = info
            visitor_menu[visitor_id] += '1'
            OM_API.OM_menuPlay(http_client, visitor_id, visitor_menu[visitor_id])
            
    elif menu == '11111':   # 挂号分支里的输入身份证号码
        if len(info) != 11:     # 身份证格式不正确，输入异常
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['id_num'] = info
            # 查询指定的科室、级别、时间已有的预约数量
            amount = DB_API.DB_queryDLTCount(db_connect, visitor_data[visitor_id])
            # 查询数据库中是否有已选时间段的同一身份证的挂号记录
            exist_regs = DB_API.DB_queryIDAtSameTime(db_connect, visitor_data[visitor_id])

            if amount < AMOUNT_LIMIT and len(exist_regs) == 0:      # 可以成功挂号的情况
                DB_API.DB_insert(db_connect, visitor_data[visitor_id])
                voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.regSuccess)
                voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.byebye)
                OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)

            elif amount >= AMOUNT_LIMIT:    # 预约满了
                cmd_list = [OM_API.regFail, OM_API.selectAnotherTime, OM_API.byebye]
                for x in cmd_list:
                    voice_cmd = OM_API.OM_addVoice(voice_cmd, x)
                OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)

            elif len(exist_regs) >= 0:      # 已存在同身份证预约
                department_voice = department_map[exist_regs[0][0]]
                cmd_list = [OM_API.existData, department_voice, OM_API.pleaseCancel, OM_API.byebye]
                for x in cmd_list:
                    voice_cmd = OM_API.OM_addVoice(voice_cmd, x)
                OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)

    elif menu == '12':  # 查询挂号服务
        if len(info) != 11:     # 身份证格式不正确，输入异常
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['id_num'] = info
            # 获得数据库中，该身份证号的挂号记录
            regs = DB_API.DB_queryID(db_connect, visitor_data[visitor_id]['id_num'])

            # 暂时只处理第一条记录
            time_string = regs[0][2]

            time_voice = ""
            period = time_period(time_string)  # 今天 or 明天 or 后天 / 上午 or 下午
            if period == 5:     # 今天上午
                time_voice = OM_API.today + '+' + OM_API.morning
            elif period == 6:   # 今天下午
                time_voice = OM_API.today + '+' + OM_API.afternoon
            elif period == 1:   # 明天上午
                time_voice = OM_API.tomorrow + '+' + OM_API.morning
            elif period == 2:   # 明天下午
                time_voice = OM_API.tomorrow + '+' + OM_API.afternoon
            elif period == 3:   # 后天上午
                time_voice = OM_API.afterTomorrow + '+' + OM_API.morning
            elif period == 4:   # 后天下午
                time_voice = OM_API.afterTomorrow + '+' + OM_API.afternoon
            else:   # 挂号过期或异常
                pass
            
            if time_string == "":   # 存在有效挂号记录
                visitor_menu[visitor_id] += '1'
                department_voice = department_map[regs[0][0]]
                level_voice = level_voice_map[regs[0][1]]

                cmd_list = [OM_API.existData, department_voice, level_voice, time_voice, 
                            OM_API.chooseConfirmCancel, OM_API.chooseRepeat, OM_API.chooseTop]
                for x in cmd_list:
                    voice_cmd = OM_API.OM_addVoice(voice_cmd, x)
                OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)

            else:   # 不存在有效挂号记录
                cmd_list = [OM_API.noData, OM_API.byebye]
                for x in cmd_list:
                    voice_cmd = OM_API.OM_addVoice(voice_cmd, x)
                OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)


    elif menu == '121': # 是否取消挂号
        if info not in ['1']:   # 输入有误
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            # 删除挂号记录
            DB_API.DB_delete(db_connect, visitor_data[visitor_id]['id_num'])
            cmd_list = [OM_API.canceled, OM_API.byebye]
            for x in cmd_list:
                voice_cmd = OM_API.OM_addVoice(voice_cmd, x)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)




# 用于构建http服务器需要实现的子类
class MyHTTPRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self) -> None:
        content = self.rfile.read(int(self.headers['content-length']))
        dom = minidom.parseString(content)

        print(content.decode())

        root = dom.getElementsByTagName('Event')
        if not root:  return

        root = root[0]
        visitor = root.getElementsByTagName('visitor')
        if not visitor: return

        visitor = visitor[0]
        visitor_id = visitor.attributes['id'].value

        # 根据不同事件类型分别处理
        if root.attributes['attribute'].value == 'INCOMING':    # 来电
            visitor_data[visitor_id] = {}
            visitor_menu[visitor_id] = '1'
            OM_API.OM_menuPlay(http_client, visitor_id, visitor_menu[visitor_id])
        
        elif root.attributes['attribute'].value == 'EndOfAnn':  # 语音播放完了
            pass

        elif root.attributes['attribute'].value == 'DTMF':      # 按键输入
            info = visitor.getElementsByTagName('info')[0].childNodes[0].data[:-1]
            bussiness_process(visitor_id, info)                 # 业务逻辑


if __name__ == "__main__":
    OM_API.OM_menuConfig(http_client)       # 设置语音菜单
    httpd = HTTPServer(HOST_ADDR, MyHTTPRequestHandler)     # 初始化http服务器
    httpd.serve_forever()       # http 服务保持运行
