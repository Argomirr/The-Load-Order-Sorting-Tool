from distutils.core import setup
import py2exe

setup(
    console = [
        {
            "script": "LOST Launcher.py",                    ### Main Python script    
            "icon_resources": [(0x0004, "lost.ico")]     ### Icon to embed into the PE file.
        }
    ],
)