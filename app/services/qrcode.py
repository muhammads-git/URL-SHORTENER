import qrcode as qr


""" using class for qrcode
in-case we need to do other than just making qrcode
each function will be in the same class.
"""

class QRCODE:
   def generateQRcode(self,url):
      qrcode = qr.make(url)
      return qrcode
   
   

   

