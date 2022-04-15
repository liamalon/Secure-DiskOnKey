__author__ = "Liam Alon"
__date__ = "25/02/2022"
import shutil
import os
from unittest.mock import patch

_os_path_isfile = os.path.isfile

def accept(path):
   if "Asset" in path or "EVERYTHING.zip" in path or "SSDclient.py" in path:
      return False
   return _os_path_isfile(path)

def zip_all(path,name):
   """
   --> Zip all of the files to one file <-- 
   """

   """
   to do everything
   shutil.make_archive("EVERYTHING", 'zip', CURRENT_DISK)
   """
   with patch("os.path.isfile", side_effect=accept):
        shutil.make_archive(name, "zip", path)
   print("zipped")

def unzip_all(path,name):
   """
   --> Unzip the file to get the original Files <-- 
   """

   """
   to do everything
   shutil.make_archive("EVERYTHING", 'zip', CURRENT_DISK)
   """
   
   shutil.unpack_archive(name,path)
   print("unzipped")

if __name__ == "__main__":
   zip_all(os.getcwd())