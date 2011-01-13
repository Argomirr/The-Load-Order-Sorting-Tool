; Based on the ModernUI example script - it's a real mess, but it works

;--------------------------------
;Include Modern UI
	SetCompressor lzma
  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
	Name "The Load Order Sorting Tool"
	OutFile "LOST_rev100_exe_installer.exe"
	VIProductVersion 0.1.0.0
	VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "LOST"
	VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "Argomirr"
	VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© Argomirr"
	VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "LOST installer"
	VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "1.0.0"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\The Load Order Sorting Tool"

  ;Get installation folder from registry if available
;  InstallDirRegKey HKCU "Software\Modern UI Test" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING
 ; !define MUI_ICON "lost.ico"
  !define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\win.bmp"
  !define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\lost.bmp"

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "C:\LOST\License.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
	!insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections
Section "LOST (required)" Main

	SectionIn RO
	SetOutPath "$INSTDIR"

  ;ADD YOUR OWN FILES HERE...
	File "bz2.pyd"
	File "library.zip"
	File "LOST Launcher.exe"
	File "lost.ico"
	File "msvcp90.dll"
	File "python26.dll"
	File "select.pyd"
	File "settings.ini"
	File "unicodedata.pyd"
	File "w9xpopen.exe"
	File "wx._controls_.pyd"
	File "wx._core_.pyd"
	File "wx._gdi_.pyd"
	File "wx._html.pyd"
	File "wx._misc_.pyd"
	File "wx._windows_.pyd"
	File "wxbase28uh_net_vc.dll"
	File "wxbase28uh_vc.dll"
	File "wxmsw28uh_adv_vc.dll"
	File "wxmsw28uh_core_vc.dll"
	File "wxmsw28uh_html_vc.dll"
	File "_socket.pyd"
	File "_ssl.pyd"

  ;Store installation folder
;  WriteRegStr HKCU "Software\Modern UI Test" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

Section "Source code" src

  SetOutPath "$INSTDIR\src"

  ;ADD YOUR OWN FILES HERE...
	File "src\LOST Launcher.py"
	File "src\meat.py"
	File "src\loadorder2.py"
	File "src\boss.py"
	
SectionEnd

Section "Shortcut" shortcut
   
    ;Create shortcuts
    CreateShortCut "$DESKTOP\LOST.lnk" "$INSTDIR\LOST Launcher.exe"
  
SectionEnd


;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_Main ${LANG_ENGLISH} "The LOST application. This must be installed in order for LOST to work."
  LangString DESC_src ${LANG_ENGLISH} "Source code for LOST. If you are interested in taking a look at the internals, select this option to install the source code."
  LangString DESC_shortcut ${LANG_ENGLISH} "Create a shortcut to LOST on your desktop."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${Main} $(DESC_Main)
	!insertmacro MUI_DESCRIPTION_TEXT ${src} $(DESC_src)
	!insertmacro MUI_DESCRIPTION_TEXT ${shortcut} $(DESC_shortcut)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
	Delete "$INSTDIR\bz2.pyd"
	Delete "$INSTDIR\library.zip"
	Delete "$INSTDIR\LOST Launcher.exe"
	Delete "$INSTDIR\lost.ico"
	Delete "$INSTDIR\msvcp90.dll"
	Delete "$INSTDIR\python26.dll"
	Delete "$INSTDIR\select.pyd"
	Delete "$INSTDIR\settings.ini"
	Delete "$INSTDIR\unicodedata.pyd"
	Delete "$INSTDIR\w9xpopen.exe"
	Delete "$INSTDIR\wx._controls_.pyd"
	Delete "$INSTDIR\wx._core_.pyd"
	Delete "$INSTDIR\wx._gdi_.pyd"
	Delete "$INSTDIR\wx._html.pyd"
	Delete "$INSTDIR\wx._misc_.pyd"
	Delete "$INSTDIR\wx._windows_.pyd"
	Delete "$INSTDIR\wxbase28uh_net_vc.dll"
	Delete "$INSTDIR\wxbase28uh_vc.dll"
	Delete "$INSTDIR\wxmsw28uh_adv_vc.dll"
	Delete "$INSTDIR\wxmsw28uh_core_vc.dll"
	Delete "$INSTDIR\wxmsw28uh_html_vc.dll"
	Delete "$INSTDIR\_socket.pyd"
	Delete "$INSTDIR\_ssl.pyd"
	
	Delete "$INSTDIR\src\LOST Launcher.py"
	Delete "$INSTDIR\src\meat.py"
	Delete "$INSTDIR\src\loadorder2.py"
	Delete "$INSTDIR\src\boss.py"
	
	Delete "$DESKTOP\LOST.lnk"
	
  Delete "$INSTDIR\Uninstall.exe"

  RMDir "$INSTDIR\src"
  RMDir "$INSTDIR"

;  DeleteRegKey /ifempty HKCU "Software\Modern UI Test"

SectionEnd
