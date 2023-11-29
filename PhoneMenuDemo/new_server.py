#########################################################################
# create on 2023-11-29
# @author: Violeta, email: violet2021@foxmail.com
# brief: a hospital appointment server through handling OM IVR menu

#########################################################################
# custom config here

OM_IP = "10.16.18.150"  # your OM device's ip
HOST_ADDR = ("10.230.32.122", 8989) # your machine's ip and port

#########################################################################
# don't modify the following content unless you do realize what will happen

MENU_VOICE_MAP = {
    '1': 'user_top',
    '2': 'user_date',
    '3': 'user_doctor_level',
    '4': 'user_registering',
    '5': 'user_success',
    '6': 'user_fail',
    '7': 'user_thank_bye',
    '8': 'user_timeout'
}

import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from http.client import HTTPConnection
from xml.dom import minidom

http_client = HTTPConnection(OM_IP)
db_connect = sqlite3.connect("appointments.db")
db_cusor = db_connect.cursor()
visitor_menu = {}
visitor_appointment_detail = {}

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
            self.transfer_menu(visitor_id, '1')
            visitor_appointment_detail[visitor_id] = {}
        
        elif root.attributes['attribute'].value == 'EndOfAnn':
            self.byebye(visitor_id)

        elif root.attributes['attribute'].value == 'DTMF':
            info = visitor.getElementsByTagName('info')[0].childNodes[0].data
            menu = visitor_menu[visitor_id]

            if info == '0':     # real human serving 人工服务
                self.transfer_ext(visitor_id, '6213')
                return
            elif info == '*':
                if 1 < int(menu) < 4:     # 返回上一级菜单
                    self.transfer_menu(visitor_id, str(int(menu) - 1))
                elif menu == '1':
                    self.transfer_menu(visitor_id, menu)
                return
            elif info == 'T':   # 超时无按键输入挂断
                self.byebye(visitor_id)
                return

            if menu == '1':     # select department  选择科室
                visitor_appointment_detail[visitor_id]['department'] = info
                self.transfer_menu(visitor_id, '2')
            elif menu == '2':    # select date  选择日期
                visitor_appointment_detail[visitor_id]['date'] = info
                self.transfer_menu(visitor_id, '3')
            elif menu == '3':    # select doctor level  选择医师级别 （普通/专家）
                visitor_appointment_detail[visitor_id]['level'] = info
                self.transfer_menu(visitor_id, '4')
            elif menu == '4':    # waiting for registering 挂号中，请稍候
                pass
            else:
                return
            self.transfer_menu(visitor_id, str(int(menu) + 1))
            print(visitor_appointment_detail)
            
    
    def transfer_menu(self, visitor_id: str, menu_id: str, voice_file:str = None) -> None:
        visitor_menu[visitor_id] = menu_id

        dom, root = self.create_dom(visitor_id, 'menu', menu_id)
        if voice_file != None:
            voicefile = dom.createElement('voicefile')
            voicefile.appendChild(dom.createTextNode(voice_file))
            root.appendChild(voicefile)
        # print(dom.toprettyxml(encoding='utf-8').decode())

        self.http_request(dom)
    
    def transfer_ext(self, visitor_id: str, ext_id: str) -> None:
        dom, _ = self.create_dom(visitor_id, 'ext', ext_id)
        # print(dom.toprettyxml(encoding='utf-8').decode())

        self.http_request(dom)

    def byebye(self, visitor_id: str):
        dom = minidom.Document()
        root = dom.createElement('Control')
        root.setAttribute('attribute', 'Clear')
        dom.appendChild(root)

        visitor = dom.createElement('visitor')
        visitor.setAttribute('id', visitor_id)
        root.appendChild(visitor)

        self.http_request(dom)


    def create_dom(self, visitor_id: str, elem_type: str, elem_id: str) -> list:
        dom = minidom.Document()
        root = dom.createElement('Transfer')
        root.setAttribute('attribute', 'Connect')
        dom.appendChild(root)

        visitor = dom.createElement('visitor')
        visitor.setAttribute('id', visitor_id)
        root.appendChild(visitor)

        elem = dom.createElement(elem_type)
        elem.setAttribute('id', elem_id)
        root.appendChild(elem)

        return dom, root
    
    def http_request(self, dom: minidom.Document) -> None:
        http_client.connect()
        http_client.request('POST', '/xml', dom.toprettyxml(encoding='utf-8'))
        # response = http_client.getresponse()
        # print(response.read().decode())
        http_client.close()


if __name__ == "__main__":
    httpd = HTTPServer(HOST_ADDR, MyHTTPRequestHandler)
    httpd.serve_forever()
