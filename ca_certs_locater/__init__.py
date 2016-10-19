#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ca_certs_locater\__init__.py
from certifi import where

def get():
    return where()
