' Dead Cells Daily Run Silent Launcher
' Starts the emulator server in background without a black CMD window, then launches Dead Cells.

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strDir

' Determine executable: default deadcells.exe, fallback deadcells_gl.exe
strExe = strDir & "\deadcells.exe"
If Not fso.FileExists(strExe) Then
    If fso.FileExists(strDir & "\deadcells_gl.exe") Then
        strExe = strDir & "\deadcells_gl.exe"
    End If
End If

' Start Daily Run emulator server silently via pythonw
WshShell.Run "pythonw.exe """ & strDir & "\daily_server.py""", 0, False

' Launch Dead Cells and wait for exit
If fso.FileExists(strExe) Then
    WshShell.Run """" & strExe & """", 1, True
Else
    MsgBox "deadcells.exe not found in " & strDir, 16, "DailyCells Error"
End If
