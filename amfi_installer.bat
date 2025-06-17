@echo off
echo ========================================
echo      INSTALACAO ADD-IN AMFI v1.0
echo    Calculadora de Debentures AMFI
echo ========================================
echo.

REM Obter pasta atual do script
set "PASTA_ATUAL=%~dp0"
echo Script executado em: %PASTA_ATUAL%
echo.

REM Verificar se o arquivo amfi.xlam existe na mesma pasta do script
if not exist "%PASTA_ATUAL%amfi.xlam" (
    echo ERRO: Arquivo amfi.xlam nao encontrado!
    echo.
    echo O arquivo amfi.xlam deve estar na MESMA PASTA que este script:
    echo %PASTA_ATUAL%
    echo.
    echo Estrutura esperada:
    echo %PASTA_ATUAL%
    echo ├── Instalar-AMFI.bat  (este arquivo)
    echo ├── amfi.xlam          (arquivo do add-in)
    echo ├── LEIA-ME.txt
    echo └── Desinstalar-AMFI.bat
    echo.
    pause
    exit /b 1
)

echo Arquivo amfi.xlam encontrado: %PASTA_ATUAL%amfi.xlam
echo.

echo Criando pasta de add-ins...
if not exist "%APPDATA%\Microsoft\AddIns" mkdir "%APPDATA%\Microsoft\AddIns"

echo Copiando add-in AMFI...
copy "%PASTA_ATUAL%amfi.xlam" "%APPDATA%\Microsoft\AddIns\" >nul

if %errorlevel% neq 0 (
    echo ERRO: Falha ao copiar o arquivo!
    pause
    exit /b 1
)

echo Registrando add-in no sistema...
REM Registrar no Registry para versões do Excel
reg add "HKCU\Software\Microsoft\Office\16.0\Excel\Add-in Manager" /v "AMFI" /t REG_SZ /d "%APPDATA%\Microsoft\AddIns\amfi.xlam" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\15.0\Excel\Add-in Manager" /v "AMFI" /t REG_SZ /d "%APPDATA%\Microsoft\AddIns\amfi.xlam" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Office\14.0\Excel\Add-in Manager" /v "AMFI" /t REG_SZ /d "%APPDATA%\Microsoft\AddIns\amfi.xlam" /f >nul 2>&1

echo.
echo ========================================
echo     INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo O add-in AMFI foi instalado de:
echo ORIGEM: %PASTA_ATUAL%amfi.xlam
echo DESTINO: %APPDATA%\Microsoft\AddIns\amfi.xlam
echo.
echo COMO ATIVAR:
echo 1. Abra o Excel
echo 2. Va em: Arquivo > Opcoes > Suplementos
echo 3. Em "Gerenciar" selecione "Suplementos do Excel"
echo 4. Clique em "Ir..."
echo 5. Marque "AMFI" e clique OK
echo.
echo A funcao AmfiCalc() estara disponivel!
echo.
pause