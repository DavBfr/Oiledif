#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bluetooth
import sys
import time

def checksum(data):
  v = 0
  for c in data:
    v += ord(c)
  return -v & 0xFF


def hexdump(st, prefix=""):
  h = ""
  a = ""
  cw = 0
  for c in st:
    h += "%2.2x" % ord(c)
    if 32 <= ord(c) <= 126:
      a += c
    elif 160 <= ord(c) <= 255:
      a += '.'
    else:
      a += '.'
  print prefix+h+" | "+a

seqId = 0x80

def sendCmd(self, cmd, data=""):
  global seqId
  pkt = chr(seqId)+chr(cmd)+data
  pkt = "\x99"+chr(len(pkt)+1)+pkt+chr(checksum(pkt))
  hexdump(pkt, ">>> ")
  self.sendall(pkt)
  seqId+=1

def readCmd(self):
  s = ord(self.recv(1))
  l = ord(self.recv(1))
  d = self.recv(l)
  hexdump(chr(s)+chr(l)+d, "<<< ")
  return d[1], d[0], d[2:-1]

def connect():
  address = None
  uuids = ('00001101-0000-1000-8000-00805F9B34FB',)
  service_matches = ()

  for uuid in uuids:
    print "Try %s on %s" % (uuid, address)
    service_matches = bluetooth.find_service(uuid = uuid , address=address)
    if len(service_matches)>0:
      break;

  if len(service_matches) == 0:
      print "couldn't find the service"
      sys.exit(0)

  first_match = service_matches[0]

  port = first_match["port"]
  name = first_match["name"]
  host = first_match["host"]

  print "connecting to \"%s\" on %s/%d" % (name, host, port)

  sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
  sock.connect((host, port))

  try:
    sendCmd(sock, 0x00, "\x01\x02")
    print repr(readCmd(sock))

    sendCmd(sock, 0x08)
    print "Product : "+readCmd(sock)[2]

    sendCmd(sock, 0x13)
    print "Firmware : "+readCmd(sock)[2]

    t = time.localtime()
    sendCmd(sock, 0x11, "\x08%s%s%s%s%s%s%s" % (chr(t.tm_year/100), chr(t.tm_year%100), chr(t.tm_mon-1), chr(t.tm_mday), chr(t.tm_hour), chr(t.tm_min), chr(t.tm_sec)))
    readCmd(sock)
  finally:
    sock.close()

if __name__=='__main__':
  connect()

