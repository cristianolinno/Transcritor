# 📥 Guia de Instalação - Transcritor de Áudio

Este guia explica passo a passo como instalar e usar a ferramenta pela primeira vez.

## ✅ Pré-requisitos

Antes de começar, você precisa ter:

1. **Python 3.8 ou superior**
   - Verifique: `python --version`
   - Baixe em: https://www.python.org/downloads/

2. **FFmpeg instalado no sistema**
   - Veja instruções abaixo

## 🔧 Passo 1: Instalar FFmpeg

### Windows:
```powershell
# Opção 1: Usando winget (recomendado)
winget install --id=Gyan.FFmpeg -e

# Opção 2: Usando Chocolatey
choco install ffmpeg

# Opção 3: Download manual
# Baixe em: https://ffmpeg.org/download.html
# Extraia e adicione ao PATH do sistema
```

**⚠️ IMPORTANTE:** Após instalar o FFmpeg, **feche e reabra o terminal** para atualizar o PATH.

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

### Linux (CentOS/RHEL):
```bash
sudo yum install ffmpeg
```

### macOS:
```bash
brew install ffmpeg
```

### Verificar instalação:
```bash
ffmpeg -version
```

Se aparecer a versão do FFmpeg, está instalado corretamente!

## 📁 Passo 2: Preparar o Projeto

1. **Extraia os arquivos** (se recebeu em ZIP)
   - Você precisa dos arquivos:
     - `transcritor.py`
     - `requirements.txt`
     - `README.md`

2. **Abra o terminal** na pasta do projeto

3. **Crie o ambiente virtual:**
   ```bash
   python -m venv venv
   ```

## 🚀 Passo 3: Ativar e Instalar

### Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

Se der erro de política de execução:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### Windows (CMD):
```cmd
venv\Scripts\activate.bat
```

### Linux/macOS:
```bash
source venv/bin/activate
```

Você saberá que está ativado quando aparecer `(venv)` no início da linha do terminal.

### Instalar dependências:
```bash
pip install -r requirements.txt
```

Isso pode levar alguns minutos na primeira vez (baixa o modelo Whisper).

## ✅ Passo 4: Testar

Teste se está funcionando:

```bash
python transcritor.py --help
```

Se aparecer a ajuda, está tudo certo! 🎉

## 🎯 Primeiro Uso

Transcreva seu primeiro áudio:

```bash
python transcritor.py seu_audio.mp3
```

Na primeira execução, o modelo Whisper será baixado automaticamente (pode levar alguns minutos).

## ❓ Problemas Comuns

### "FFmpeg não encontrado"
- Certifique-se de que o FFmpeg está instalado
- Feche e reabra o terminal
- Verifique com: `ffmpeg -version`

### "Bibliotecas não instaladas"
- Certifique-se de que o ambiente virtual está ativado
- Execute: `pip install -r requirements.txt`

### "Erro ao ativar venv no PowerShell"
- Execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Tente novamente

### Modelo demora muito para baixar
- Normal na primeira execução
- O modelo "base" tem ~140MB
- Modelos maiores demoram mais

## 📞 Precisa de Ajuda?

Consulte o `README.md` para mais informações sobre uso e opções disponíveis.

