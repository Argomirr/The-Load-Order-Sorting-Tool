from distutils.core import setup
import py2exe

setup(
    windows = [
        {
            "script": "LOST Launcher.py",                    ### Main Python script    
            "icon_resources": [(1, "lost32x32.ico")]     ### Icon to embed into the PE file.
        }
    ],
)