@echo off
echo ========================================
echo     DESINSTALACAO ADD-IN AMFI v1.0
echo ========================================
echo.

echo Removendo arquivo do add-in...
if exist "%APPDATA%\Microsoft\AddIns\amfi.xlam" (
    del "%APPDATA%\Microsoft\AddIns\amfi.xlam"
    echo Arquivo removido com sucesso.
) else (
    echo Arquivo nao encontrado.
)

echo Removendo registros do sistema...
reg delete "HKCU\Software\Microsoft\Office\16.0\Excel\Add-in Manager" /v "AMFI" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Office\15.0\Excel\Add-in Manager" /v "AMFI" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Office\14.0\Excel\Add-in Manager" /v "AMFI" /f >nul 2>&1

echo.
echo ========================================
echo    DESINSTALACAO CONCLUIDA!
echo ========================================
echo.
echo O add-in AMFI foi removido do sistema.
echo Se o Excel estiver aberto, feche e reabra para que
echo as alteracoes tenham efeito.
echo.
pause