#!/usr/bin/python
# -*- conding: utf-8
"""
Creat on 2016-11-2
@author yrh

"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
from http.client import HTTPConnection
from xml.dom import minidom


visitor_menu = {}


class MenuHandler(SimpleHTTPRequestHandler):
    """

    """

    def do_GET(self):
        content = self.rfile.read(int(self.headers['content-length']))
        print(content.decode())
        dom = minidom.parseString(content)
        root = dom.getElementsByTagName('Event')
        if len(root) == 0:
            return

        root = root[0]
        visitor = root.getElementsByTagName('visitor')
        if len(visitor) == 0:
            return
        visitor = visitor[0]
        visitor_id = visitor.attributes['id'].value

        if root.attributes['attribute'].value == 'INCOMING':
            transfer_menu(visitor_id, '1', 'user_top')
        elif root.attributes['attribute'].value == 'DTMF':
            info = visitor.getElementsByTagName('info')[0].childNodes[0].data
            menu = visitor_menu[visitor_id]
            next_menu_id = '0'
            if menu == '0':
                if info == '1':
                    next_menu_id = '1'
                if info == '2':
                    next_menu_id = '2'
                if info == '3':
                    next_menu_id = '3'
            elif menu == '1':
                if info == '1':
                    next_menu_id = '11'
                elif info == '2':
                    next_menu_id = '12'
                elif info == '3':
                    next_menu_id = '13'
            elif menu == '2':
                if info == '1':
                    next_menu_id = '21'
                elif info == '2':
                    next_menu_id = '22'
                elif info == '3':
                    next_menu_id = '23'
            transfer_menu(visitor.attributes['id'].value, next_menu_id, 'user' + next_menu_id)


hostURL = '10.16.18.150'


def transfer_menu(visitor_id, menu_id, vf):
    if menu_id == '0':
        vf = 'user_top'
    visitor_menu[visitor_id] = menu_id

    dom = minidom.Document()
    root = dom.createElement('Transfer')
    root.setAttribute('attribute', 'Connect')
    dom.appendChild(root)

    visitor = dom.createElement('visitor')
    visitor.setAttribute('id', visitor_id)
    root.appendChild(visitor)

    menu = dom.createElement('menu')
    menu.setAttribute('id', menu_id)
    root.appendChild(menu)

    voicefile = dom.createElement('voicefile')
    voicefile.appendChild(dom.createTextNode(vf))
    root.appendChild(voicefile)

    print(dom.toprettyxml(encoding='utf-8').decode())

    connection = HTTPConnection(hostURL)
    connection.request('POST', '/xml', dom.toprettyxml(encoding='utf-8'))
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()


if __name__ == '__main__':
    httpd = HTTPServer(('10.230.32.122', 8989), MenuHandler)
    httpd.serve_forever()
    # test()
