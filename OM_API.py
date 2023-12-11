
from http.client import HTTPConnection
from xml.dom import minidom

# constant strings
chooseRegisterOrCancel = "user_chooseRegOrCan"

chooseHuman         = "user_chooseHuman"

chooseDepartment    = "user_chooseDepartment"
chooseLevel         = "user_chooseLevel"
chooseTime          = "user_chooseTime"
chooseRepeat        = "user_chooseRepeat"
chooseTop           = "user_chooseTop"
chooseRegisterTop   = "user_chooseRegisterTop"
chooseLastMenu      = "user_chooseLastMenu"

chooseConfirmCancel = "user_chooseConfirmCancel"   # 确认取消请按1

inputIDnumber       = "user_inputIDnumber"
error               = "user_error"
byebye              = "user_byebye"

existData           = "user_existData"      # 该时段内您已有挂号记录：（）
noData              = "user_noData"
pleaseCancel        = "user_pleaseCancel"   # 若要重新预约请先取消

regSuccess          = "user_regSuccess"
regFail             = "user_regFail"
selectAnotherTime   = "user_selectAnotherTime"

confirm             = "user_confirm"        # 确认请按#

canceled            = "user_canceled"       # 已取消预约

year                = "user_year"
month               = "user_month"
day                 = "user_day"

waike   = "user_waike"
neike   = "user_neike"
erke    = "user_erke"
wuguanke = "user_wuguanke"
pifuke  = "user_pifuke" 


def OM_createVoiceCmd() -> str:
    return ""

def OM_addVoice(cmd:str, new_cmd:str) -> str:
    if len(cmd) == 0:    return new_cmd
    else:   return cmd + "+" + new_cmd

def OM_menuPlay(web_handle:HTTPConnection, visitor_id:str, menu:str) -> None:
    
    cmd_list = []
    if   menu == '1':
        cmd_list = [chooseRegisterOrCancel, chooseHuman, chooseRepeat, confirm]
    elif menu == '11':
        cmd_list = [chooseDepartment, chooseLastMenu, chooseRepeat, confirm]
    elif menu == '111':
        cmd_list = [chooseLevel, chooseLastMenu, chooseRepeat, confirm]
    elif menu == '1111':
        cmd_list = [chooseTime, chooseLastMenu, chooseRepeat, confirm,]
    elif menu == '11111':
        cmd_list = [inputIDnumber]
    elif menu == '12':
        cmd_list = [inputIDnumber]
    else:
        assert False
    
    cmd = ""
    for x in cmd_list:
        cmd = OM_addVoice(cmd, x)

    OM_voicePlay(web_handle, visitor_id, cmd)


def OM_voicePlay(web_handle:HTTPConnection, visitor_id:str, voice_cmd:str) -> None:
    '''
    控制 OM 设备向指定会话播放指定语音
    '''
    # input security check
    assert type(web_handle) == HTTPConnection
    assert type(visitor_id) == str and visitor_id != ""
    assert type(voice_cmd)  == str and voice_cmd  != ""
    assert voice_cmd.count('+') <= 9

    dom = minidom.Document()
    root = dom.createElement('Transfer')
    root.setAttribute('attribute', 'Connect')
    dom.appendChild(root)

    visitor = dom.createElement('visitor')
    visitor.setAttribute('id', visitor_id)
    root.appendChild(visitor)

    menu = dom.createElement('menu')
    menu.setAttribute('id', '1')
    root.appendChild(menu)

    voicefile = dom.createElement('voicefile')
    voicefile.appendChild(dom.createTextNode(voice_cmd))
    root.appendChild(voicefile)

    print(dom.toprettyxml(encoding='utf-8').decode())

    web_handle.connect()
    web_handle.request('POST', '/xml', dom.toprettyxml(encoding='utf-8'))
    web_handle.close()

def OM_menuConfig(web_handle:HTTPConnection) -> None:
    assert type(web_handle) == HTTPConnection

    dom = minidom.Document()
    root = dom.createElement('Control')
    root.setAttribute('attribute', 'Assign')
    dom.appendChild(root)

    menu = dom.createElement('menu')
    menu.setAttribute('id', '1')

    voicefile = dom.createElement('voicefile')
    voicefile.appendChild(dom.createTextNode("welcome"))
    menu.appendChild(voicefile)
    
    repeat = dom.createElement('repeat')
    repeat.appendChild(dom.createTextNode("1"))
    menu.appendChild(repeat)

    infolength = dom.createElement('infolength')
    infolength.appendChild(dom.createTextNode("12"))
    menu.appendChild(infolength)

    exit = dom.createElement('exit')
    exit.appendChild(dom.createTextNode("#"))
    menu.appendChild(exit)

    root.appendChild(menu)

    print(dom.toprettyxml(encoding='utf-8').decode())

    web_handle.connect()
    web_handle.request('POST', '/xml', dom.toprettyxml(encoding='utf-8'))
    web_handle.close()
