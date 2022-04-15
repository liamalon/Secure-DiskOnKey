__author__ = "Liam Alon"
__date__ = "25/02/2022"
import shutil
import os
from unittest.mock import patch

_os_path_isfile = os.path.isfile

STATE = None

def accept(path):
   """
   --> Which files to zip according to the state of zipping <--
   """
   if STATE == "BACKUP":
      if "Backup.zip" in path :
         return False

   elif STATE == "EVERYTHING":
      if "Asset" in path or "EVERYTHING.zip" in path or "SSDclient.py" in path :
         return False
            
   return _os_path_isfile(path)

def zip_all(path,name):

   """
   --> Zip all of the files to one file <-- 
   """

   global STATE

   STATE = name
   
   with patch("os.path.isfile", side_effect=accept):
        shutil.make_archive(name, "zip", path)

   print("zipped")

def unzip_all(path,name):
   """
   --> Unzip the file to get the original Files <-- 
   """

   shutil.unpack_archive(name,path)

   print("unzipped")

if __name__ == "__main__":
   zip_all(os.getcwd())