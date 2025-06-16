@echo off
setlocal
cls
echo ==========================================================
echo  SCRIPT DE CONFIGURACAO DE AMBIENTE VIRTUAL PARA WINDOWS
echo ==========================================================
echo.

:: 1. Verifica se o Python esta disponivel
echo Verificando a instalacao do Python...
py -V >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado. Verifique se o 'py.exe' esta instalado e no PATH do sistema.
    pause
    exit /b
)
echo Python encontrado.
echo.

:: 2. Cria o ambiente virtual
echo [1/3] Criando o ambiente virtual na pasta 'venv'...
py -m venv venv
if not exist ".\venv\Scripts\pip.exe" (
    echo ERRO: Falha ao criar o ambiente virtual 'venv'.
    pause
    exit /b
)
echo Ambiente 'venv' criado com sucesso.
echo.

:: 3. Atualiza o pip e instala os pacotes DENTRO do venv
echo [2/3] Atualizando o pip e instalando pacotes do requirements.txt...
:: Chama diretamente o python.exe e o pip.exe de dentro do venv
.\venv\Scripts\python.exe -m pip install --upgrade pip >nul
.\venv\Scripts\pip.exe install -r requirements.txt
echo Pacotes instalados com sucesso.
echo.

:: 4. Exibe as instrucoes finais para o usuario
echo [3/3] Processo finalizado!
echo.
echo =================================================================================
echo  O ambiente foi preparado com sucesso!
echo.
echo  IMPORTANTE: Para comecar a usar, voce precisa ATIVAR o ambiente no seu terminal.
echo  Execute o seguinte comando:
echo.
echo     .\venv\Scripts\Activate.ps1
echo.
echo  Apos ativar, seu prompt devera mostrar '(venv)' no inicio da linha.
echo =================================================================================
echo.
pause