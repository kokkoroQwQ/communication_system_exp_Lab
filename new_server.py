#########################################################################
# create on 2023-11-29
# @author: Violeta, email: violet2021@foxmail.com
# brief: a hospital appointment server through handling OM IVR menu
# Note: shutdown your firewall before you activate this script

#########################################################################
# custom config here

OM_IP = "10.16.18.150"  # your OM device's ip
HOST_ADDR = ("10.230.32.134", 8989) # your machine's ip and port

#########################################################################
# Don't modify the following content 
# unless you do understand what will happen

import sqlite3
import OM_API
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

http_client = HTTPConnection(OM_IP)
db_connect = sqlite3.connect("registers.db")
db_cusor = db_connect.cursor()
visitor_menu = {}
visitor_appointment_detail = {}
visitor_data = {}



def queryQuota() -> int:
    return 1

def queryTimeAndID() -> str:
    return None

def DB_register() -> None:
    pass
        

def bussiness_process(visitor_id:str, info:str) -> None:
    menu = visitor_menu[visitor_id]
    voice_cmd = OM_API.OM_createVoiceCmd()

    if info == '*':     # 返回上一级菜单
        menu = menu[:-1] if menu != '1' else menu
        visitor_menu[visitor_id] = menu
        OM_API.OM_menuPlay(http_client, visitor_id, menu)
        return
    elif info == '0':   # 重复当前菜单
        OM_API.OM_menuPlay(http_client, visitor_id, menu)
        return
    elif info == '9':   # 人工服务
        return
    elif info == 'T':   # 超时无按键输入挂断
        return

    if menu == '1':     # 挂号还是取消挂号
        if info not in ['1', '2']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            menu += info
            visitor_menu[visitor_id] = menu
            OM_API.OM_menuPlay(http_client, visitor_id, menu)

    elif menu == '11':  # 选择科室
        if info not in ['1', '2', '3', '4', '5']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['department'] = info
            menu += '1'
            visitor_menu[visitor_id] = menu
            OM_API.OM_menuPlay(http_client, visitor_id, menu)

    elif menu == '111':  # 选择普通 or 专家门诊
        if info not in ['1', '2']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['level'] = info
            menu += '1'
            visitor_menu[visitor_id] = menu
            OM_API.OM_menuPlay(http_client, visitor_id, menu)
    
    elif menu == '1111':  # 选择时间段
        if info not in ['1', '2', '3', '4']:
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:   # 查询数据库
            visitor_data[visitor_id]['time'] = info
            if queryQuota() < 1:    # 无名额，挂号失败, 重新选择时间
                OM_API.OM_voicePlay(http_client, visitor_id, OM_API.regFail)
                # OM_API.OM_voicePlay(http_client, visitor_id, OM_API.selectAnotherTime)
                OM_API.OM_menuPlay(http_client, visitor_id, menu)
            else:   # 有名额，让用户输入身份证号码
                menu += '1'
                visitor_menu[visitor_id] = menu
                OM_API.OM_voicePlay(http_client, visitor_id, OM_API.inputIDnumber)
            
    elif menu == '11111':   # 挂号分支里的输入身份证号码
        if len(info) != 11:     # 身份证格式不正确，输入异常
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['id_num'] = info
            query_result = queryTimeAndID()     # '1' '2' '3' '4' '5'
            if query_result == None:
                DB_register()
                voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.regSuccess)
                voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.byebye)
                OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
            else:
                department_voice = department_map[query_result]
                voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.existData)
                voice_cmd = OM_API.OM_addVoice(voice_cmd, department_voice)
                voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.pleaseCancel)
                voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.byebye)
                OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
    
    elif menu == '12':  # 查询挂号服务
        if len(info) != 11:     # 身份证格式不正确，输入异常
            voice_cmd = OM_API.OM_addVoice(voice_cmd, OM_API.error)
            OM_API.OM_voicePlay(http_client, visitor_id, voice_cmd)
        else:
            visitor_data[visitor_id]['id_num'] = info







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

        if root.attributes['attribute'].value == 'INCOMING':
            visitor_data[visitor_id] = {}
            visitor_menu[visitor_id] = '1'
            OM_API.OM_menuPlay(http_client, visitor_id, visitor_menu[visitor_id])
        
        elif root.attributes['attribute'].value == 'EndOfAnn':
            pass

        elif root.attributes['attribute'].value == 'DTMF':
            info = visitor.getElementsByTagName('info')[0].childNodes[0].data[:-1]
            bussiness_process(visitor_id, info)


if __name__ == "__main__":
    OM_API.OM_menuConfig(http_client)
    httpd = HTTPServer(HOST_ADDR, MyHTTPRequestHandler)
    httpd.serve_forever()
