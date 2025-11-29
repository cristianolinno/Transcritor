# 🎤 Transcritor de Áudio

Ferramenta simples e poderosa para transcrever áudios em texto usando inteligência artificial (OpenAI Whisper).

## 📋 Funcionalidades

- ✅ **Versão Web** com interface visual moderna (drag & drop)
- ✅ **Menu interativo** amigável para usuários leigos
- ✅ Transcreve áudios em diversos formatos (MP3, WAV, M4A, OGG, FLAC)
- ✅ Suporta múltiplos idiomas (português, inglês, espanhol, etc.)
- ✅ Busca palavras específicas no texto transcrito
- ✅ Modelos de diferentes tamanhos (tiny, base, small, medium, large)
- ✅ Detecção automática de idioma
- ✅ Interface de linha de comando para usuários avançados

## 🌐 Versão Web (Recomendado - Sem Instalação)

A versão web está disponível e pode ser acessada sem instalar nada! 

**Características:**
- 🎨 Interface moderna e intuitiva
- 📤 Upload por drag & drop
- ⚙️ Configurações fáceis na barra lateral
- 💾 Download da transcrição em .txt
- 📊 Estatísticas do texto transcrito

**Para disponibilizar a versão web:**
Veja o guia completo em [DEPLOY_WEB.md](DEPLOY_WEB.md)

**Testar localmente:**
```bash
pip install streamlit
streamlit run app.py
```

## 🚀 Como Usar (Instalação Local)

### 1. Clonar o Repositório

```bash
git clone https://github.com/cristianolinno/Transcritor.git
cd Transcritor
```

### 2. Instalar Dependências

Siga as instruções detalhadas no arquivo [INSTALACAO.md](INSTALACAO.md)

**Resumo rápido:**
- Instale o FFmpeg (necessário para processar áudio)
- Crie um ambiente virtual: `python -m venv venv`
- Ative o ambiente virtual
- Instale as dependências: `pip install -r requirements.txt`

### 3. Usar o Transcritor

#### 🖱️ Menu Interativo (Recomendado para Iniciantes)

Para usuários que preferem uma interface mais amigável, execute sem argumentos:

```bash
python transcritor.py
```

O menu interativo oferece:
- ✅ Interface visual com opções numeradas
- ✅ Guia passo a passo
- ✅ Validação automática de arquivos
- ✅ Sugestões inteligentes de nomes de arquivo

#### ⌨️ Linha de Comando (Avançado)

Para usuários experientes que preferem comandos diretos:

```bash
# Transcrever um áudio
python transcritor.py audio.mp3

# Salvar transcrição em arquivo
python transcritor.py audio.mp3 -o transcricao.txt

# Buscar palavras específicas
python transcritor.py audio.mp3 -b "palavra1" "palavra2"

# Usar modelo maior (mais preciso)
python transcritor.py audio.mp3 -m medium

# Ver todas as opções
python transcritor.py --help
```

## 📖 Exemplos de Uso

```bash
# Transcrição simples
python transcritor.py entrevista.mp3

# Transcrição e busca
python transcritor.py podcast.mp3 -b "Python" "programação" -o resultado.txt

# Modelo grande para melhor precisão
python transcritor.py audio_longo.mp3 -m large -o transcricao_completa.txt
```

## 🛠️ Requisitos

- Python 3.8 ou superior
- FFmpeg instalado no sistema
- ~500MB de espaço em disco (para o modelo base)

## 📝 Opções Disponíveis

- `-o, --output`: Salvar transcrição em arquivo .txt
- `-b, --buscar`: Buscar palavras/frases no texto
- `-m, --modelo`: Escolher modelo (tiny, base, small, medium, large)
- `-i, --idioma`: Especificar idioma (pt, en, es, etc.) ou "auto"
- `-c, --case-sensitive`: Busca diferencia maiúsculas/minúsculas

## 📄 Licença

Veja o arquivo [LICENSE](LICENSE) para mais detalhes.


