# 🌐 Como Disponibilizar a Versão Web

Este guia explica como disponibilizar o Transcritor de Áudio na web de forma **gratuita** usando Streamlit Cloud.

## 🚀 Opção 1: Streamlit Cloud (Mais Fácil - Recomendado)

### Pré-requisitos:
- ✅ Conta no GitHub (gratuita)
- ✅ Repositório público no GitHub
- ✅ Conta no Streamlit Cloud (gratuita)

### Passo a Passo:

1. **Certifique-se de que seu repositório está no GitHub**
   ```bash
   git add .
   git commit -m "Adiciona versão web com Streamlit"
   git push origin main
   ```

2. **Acesse o Streamlit Cloud**
   - Vá para: https://streamlit.io/cloud
   - Clique em "Sign up" ou "Get started"
   - Faça login com sua conta do GitHub

3. **Conecte seu Repositório**
   - Clique em "New app"
   - Selecione seu repositório: `cristianolinno/Transcritor`
   - Branch: `main`
   - Main file path: `app.py`
   - Clique em "Deploy!"

4. **Aguarde o Deploy**
   - O Streamlit vai instalar as dependências automaticamente
   - Isso pode levar alguns minutos na primeira vez
   - Você receberá um link como: `https://seu-app.streamlit.app`

5. **Pronto! 🎉**
   - Seu app estará disponível publicamente
   - Você pode compartilhar o link com seus amigos
   - Atualizações no GitHub são deployadas automaticamente

### ⚠️ Notas Importantes:

- **FFmpeg**: O Streamlit Cloud já tem FFmpeg instalado, então não precisa se preocupar
- **Modelos Whisper**: Serão baixados automaticamente na primeira execução
- **Limites**: O plano gratuito tem alguns limites de uso, mas é suficiente para uso pessoal
- **Tempo de processamento**: Áudios grandes podem demorar (o Streamlit tem timeout de 5 minutos)

---

## 🚀 Opção 2: Railway (Alternativa)

### Passo a Passo:

1. **Acesse Railway**
   - Vá para: https://railway.app
   - Faça login com GitHub

2. **Crie um Novo Projeto**
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha seu repositório

3. **Configure o Deploy**
   - Railway detecta automaticamente que é Python
   - Adicione variável de ambiente se necessário
   - Clique em "Deploy"

4. **Configure o Comando**
   - No settings, adicione:
     - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

5. **Pronto!**
   - Railway fornece um link público
   - Atualizações automáticas do GitHub

---

## 🚀 Opção 3: Render (Alternativa)

### Passo a Passo:

1. **Acesse Render**
   - Vá para: https://render.com
   - Faça login com GitHub

2. **Crie um Novo Web Service**
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub

3. **Configure**
   - **Name**: transcritor (ou o que preferir)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

4. **Deploy**
   - Clique em "Create Web Service"
   - Aguarde o deploy

---

## 📝 Arquivo de Configuração (Opcional)

Você pode criar um arquivo `.streamlit/config.toml` para personalizar:

```toml
[server]
headless = true
port = 8501
enableCORS = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

---

## 🔧 Solução de Problemas

### Erro: "FFmpeg not found"
- No Streamlit Cloud, o FFmpeg já está instalado
- Se usar outra plataforma, pode ser necessário instalar

### Erro: "Modelo não carrega"
- Verifique se `openai-whisper` está no `requirements.txt`
- Os modelos são baixados automaticamente na primeira execução

### App muito lento
- Use modelos menores (tiny, base)
- Processe áudios menores
- O plano gratuito pode ter limitações de CPU

### Timeout
- Streamlit Cloud tem timeout de 5 minutos
- Para áudios grandes, considere usar a versão local

---

## 💡 Dicas

1. **Teste localmente primeiro:**
   ```bash
   pip install streamlit
   streamlit run app.py
   ```

2. **Monitore o uso:**
   - Streamlit Cloud mostra estatísticas de uso
   - Railway e Render também têm dashboards

3. **Customize o design:**
   - Edite o CSS no arquivo `app.py`
   - Adicione seu logo ou cores personalizadas

4. **Compartilhe o link:**
   - Depois do deploy, você terá um link público
   - Compartilhe com seus amigos!

---

## 🎉 Pronto!

Depois de fazer o deploy, você terá uma versão web do seu transcritor disponível para todos usarem, sem precisar instalar nada!

