# Remote control Netflix launcher by sytone. https://github.com/sytone
# I used Steam launcher as a guide when making this addon, plus borrowed ideas and code from it too. Big thanks to teeedubb!
import os
import sys
import subprocess
import time
import shutil
import stat
import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon(id='script.netflixremotecontroller.launcher')
addonPath = addon.getAddonInfo('path')
addonIcon = addon.getAddonInfo('icon')
addonVersion = addon.getAddonInfo('version')
dialog = xbmcgui.Dialog()
language = addon.getLocalizedString
scriptid = 'script.netflixremotecontroller.launcher'

remoteControlNetflixWin = addon.getSetting("RemoteControlNetflixWin").decode("utf-8")
kodiWin = addon.getSetting("KodiWin").decode("utf-8")

quitKodiSetting = addon.getSetting("QuitKodi")
busyDialogTime = int(addon.getSetting("BusyDialogTime"))
filePathCheck = addon.getSetting("FilePathCheck")
kodiPortable = addon.getSetting("KodiPortable")
preScriptEnabled = addon.getSetting("PreScriptEnabled")
preScript = addon.getSetting("PreScript").decode("utf-8")
postScriptEnabled = addon.getSetting("PostScriptEnabled")
postScript = addon.getSetting("PostScript").decode("utf-8")
osWin = xbmc.getCondVisibility('system.platform.windows')
osOsx = xbmc.getCondVisibility('system.platform.osx')
osLinux = xbmc.getCondVisibility('system.platform.linux')
osAndroid = xbmc.getCondVisibility('system.platform.android')
suspendAudio = addon.getSetting("SuspendAudio")

txt_encode = 'utf-8'
try:
    txt_encode = sys.getfilesystemencoding()
except:
    pass

def log(msg):
    msg = msg.encode(txt_encode)
    xbmc.log('%s: %s' % (scriptid, msg))

def getAddonInstallPath():
    path = addon.getAddonInfo('path').decode("utf-8")
    return path

def getAddonDataPath():
    path = xbmc.translatePath('special://profile/addon_data/%s' % scriptid).decode("utf-8")
    if not os.path.exists(path):
        log('addon userdata folder does not exist, creating: %s' % path)
        try:
            os.makedirs(path)
            log('created directory: %s' % path)
        except:
            log('ERROR: failed to create directory: %s' % path)
            dialog.notification(language(50123), language(50126), addonIcon, 5000)
    return path

def fileChecker():
    if filePathCheck == 'true':
        log('running program file check, option is enabled: filePathCheck = %s' % filePathCheck)
        rcnWin = addon.getSetting("RemoteControlNetflixWin")
        kodiWin = addon.getSetting("KodiWin")
        rcnExe = os.path.join(rcnWin).decode("utf-8")
        kodiExe = os.path.join(kodiWin).decode("utf-8")
        programFileCheck(rcnExe, kodiExe)
    else:
        log('skipping program file check, option disabled: filePathCheck = %s' % filePathCheck)

def fileCheckDialog(programExe):
    log('ERROR: dialog to go to addon settings because executable does not exist: %s' % programExe)
    if dialog.yesno(language(50123), programExe, language(50122), language(50121)):
        log('yes selected, opening addon settings')
        addon.openSettings()
        fileChecker()
        sys.exit()
    else:
        log('ERROR: no selected with invalid executable, exiting: %s' % programExe)
        sys.exit()


def programFileCheck(rcnExe, kodiExe):
    if os.path.isfile(os.path.join(rcnExe)):
        log('Remote Control Netflix executable exists %s' % rcnExe)
    else:
        fileCheckDialog(rcnExe)
    if os.path.isfile(os.path.join(kodiExe)):
        log('Kodi executable exists %s' % kodiExe)
    else:    
        fileCheckDialog(kodiExe)


def quitKodiDialog():
    global quitKodiSetting
    if quitKodiSetting == '2':
        log('quit setting: %s selected, asking user to pick' % quitKodiSetting)
        if dialog.yesno('Remote Control Netflix', language(50073)):
            quitKodiSetting = '0'
        else:
            quitKodiSetting = '1'
    log('quit setting selected: %s' % quitKodiSetting)


def kodiBusyDialog():
    if busyDialogTime != 0:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        log('busy dialog started')
        time.sleep(busyDialogTime)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        log('busy dialog stopped after: %s seconds' % busyDialogTime)


def rcnPrePost():
    global postScript
    global preScript
    if preScriptEnabled == 'false':
        preScript = 'false'
    elif preScriptEnabled == 'true':
        if not os.path.isfile(os.path.join(preScript)):
            log('pre-rcnPrePost script does not exist, disabling!: "%s"' % preScript)
            preScript = 'false'
            dialog.notification(language(50123), language(50126), addonIcon, 5000)
    elif preScript == '':
        preScript = 'false'
    log('pre rcnPrePost script: %s' % preScript)
    if postScriptEnabled == 'false':
        postScript = 'false'
    elif preScriptEnabled == 'true':
        if not os.path.isfile(os.path.join(postScript)):
            log('post-rcnPrePost script does not exist, disabling!: "%s"' % postScript)
            postScript = 'false'
            dialog.notification(language(50123), language(50126), addonIcon, 5000)
    elif postScript == '':
        postScript = 'false'
    log('post rcnPrePost script: %s' % postScript)


def launchRemoteControlNetflix():
    cmd = '"%s"' % (remoteControlNetflixWin) #"%s" "%s" "%s" "%s" "%s" "%s"' % (remoteControlNetflixWin, steamWin, kodiWin, quitKodiSetting, kodiPortable, preScript, postScript)
    #log('Windows UTF-8 command: "%s"' % cmdutf8)
    if addon.getSetting("smstextentry") == 'true':
        cmd = cmd + ' "smstextentry"'
    if addon.getSetting("stopbuttonquits") == 'true':
        cmd = cmd + ' "stopbuttonquits"'
    if addon.getSetting("refreshratemode") == 'true':
        cmd = cmd + ' "refreshratemode"'
    if addon.getSetting("disablenetflixstart") == 'true':
        cmd = cmd + ' "disablenetflixstart"'
    if addon.getSetting("disablenetflixquit") == 'true':
        cmd = cmd + ' "disablenetflixquit"'
    if addon.getSetting("disablefullscreen") == 'true':
        cmd = cmd + ' "disablefullscreen"'

    try:
        log('attempting to launch: %s' % cmd)
        print cmd.encode('utf-8')
        if suspendAudio == 'true':
            xbmc.audioSuspend()
            log('Audio suspended')
        if quitKodiSetting == '1' and suspendAudio == 'true':
            proc_h = subprocess.Popen(cmd.encode(txt_encode), shell=True, close_fds=False)
            kodiBusyDialog()
            log('Waiting for Remote Control Netflix to exit')
            while proc_h.returncode is None:
                xbmc.sleep(1000)
                proc_h.poll()
            log('Start resuming audio....')
            xbmc.audioResume()
            log('Audio resumed')
            del proc_h        
        else:
            subprocess.Popen(cmd.encode(txt_encode), shell=True, close_fds=True)
            kodiBusyDialog()


    except:
        log('ERROR: failed to launch: %s' % cmd)
        print cmd.encode(txt_encode)
        dialog.notification(language(50123), language(50126), addonIcon, 5000)


log('****Running Remote Control Netflix Launcher v%s....' % addonVersion)
log('running on osAndroid, osOsx, osLinux, osWin: %s %s %s %s ' % (osAndroid, osOsx, osLinux, osWin))
log('System text encoding in use: %s' % txt_encode)

if osWin:
    log('Using windows as the Nativ OS. All Good.')
    fileChecker()
    rcnPrePost()
    quitKodiDialog()
    launchRemoteControlNetflix()
else:
    log('ERROR: failed to launch not Windows!')
    dialog.notification(language(50123), language(50126), addonIcon, 5000)


