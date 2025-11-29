#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transcritor de Áudio - Versão Web
Aplicação web para transcrição de áudio usando Streamlit
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import sys

# Adiciona o diretório atual ao path para importar transcritor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Verifica FFmpeg antes de importar
import shutil
import subprocess

def verificar_ffmpeg():
    """Verifica se o FFmpeg está disponível, tentando vários métodos"""
    # Método 1: Verificar no PATH padrão
    if shutil.which("ffmpeg") is not None:
        return True
    
    # Método 2: Tentar executar diretamente (para Streamlit Cloud)
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            return True
    except:
        pass
    
    # Método 3: Verificar caminhos comuns no Linux/Streamlit Cloud
    caminhos_comuns = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/opt/conda/bin/ffmpeg",
    ]
    for caminho in caminhos_comuns:
        if os.path.exists(caminho):
            # Adiciona ao PATH se encontrar
            os.environ["PATH"] = os.path.dirname(caminho) + os.pathsep + os.environ.get("PATH", "")
            return True
    
    return False

# Verifica FFmpeg mas não bloqueia - mostra aviso
ffmpeg_disponivel = verificar_ffmpeg()

if not ffmpeg_disponivel:
    st.warning("""
    ⚠️ **FFmpeg não encontrado no PATH padrão.**
    
    O Whisper pode funcionar mesmo assim para alguns formatos (MP3, WAV, M4A).
    Se encontrar erros ao processar, pode ser necessário o FFmpeg.
    
    **Nota:** No Streamlit Cloud, o FFmpeg geralmente está disponível, mas pode não estar no PATH.
    Você pode tentar processar o áudio mesmo assim.
    """)

# Importa a classe TranscritorAudio do módulo transcritor
try:
    from transcritor import TranscritorAudio, verificar_ffmpeg as verificar_ffmpeg_transcritor
except ImportError as e:
    st.error(f"❌ Erro ao importar módulo transcritor: {str(e)}")
    st.info("💡 Verifique se todos os arquivos estão presentes e as dependências instaladas.")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="🎤 Transcritor de Áudio",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar o design
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🎤 Transcritor de Áudio</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transcreva seus áudios em texto usando inteligência artificial</p>', unsafe_allow_html=True)

# Sidebar com configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Seleção de modelo
    modelo_opcoes = {
        "Tiny (Rápido)": "tiny",
        "Base (Recomendado)": "base",
        "Small (Preciso)": "small",
        "Medium (Muito Preciso)": "medium",
        "Large (Máxima Precisão)": "large"
    }
    
    modelo_selecionado = st.selectbox(
        "🎯 Modelo Whisper",
        options=list(modelo_opcoes.keys()),
        index=1,  # Base como padrão
        help="Modelos maiores são mais precisos mas demoram mais"
    )
    modelo = modelo_opcoes[modelo_selecionado]
    
    # Seleção de idioma
    idioma_opcoes = {
        "Português": "pt",
        "Inglês": "en",
        "Espanhol": "es",
        "Francês": "fr",
        "Alemão": "de",
        "Italiano": "it",
        "Detecção Automática": None
    }
    
    idioma_selecionado = st.selectbox(
        "🌍 Idioma",
        options=list(idioma_opcoes.keys()),
        index=0,  # Português como padrão
        help="Escolha o idioma do áudio ou use detecção automática"
    )
    idioma = idioma_opcoes[idioma_selecionado]
    
    st.markdown("---")
    st.markdown("### 📝 Sobre")
    st.markdown("""
    Esta ferramenta usa o modelo Whisper da OpenAI para transcrever áudios.
    
    **Formatos suportados:**
    - MP3, WAV, M4A, OGG, FLAC
    
    **Dica:** Modelos maiores são mais precisos, mas processam mais devagar.
    """)

# Área principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Upload de Áudio")
    
    # Upload de arquivo
    arquivo_audio = st.file_uploader(
        "Arraste e solte seu arquivo de áudio aqui ou clique para selecionar",
        type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac'],
        help="Formatos suportados: MP3, WAV, M4A, OGG, FLAC, AAC"
    )
    
    if arquivo_audio is not None:
        # Mostra informações do arquivo
        st.info(f"📄 Arquivo selecionado: **{arquivo_audio.name}** ({arquivo_audio.size / 1024 / 1024:.2f} MB)")
        
        # Opção de salvar arquivo
        salvar_arquivo = st.checkbox("💾 Salvar transcrição em arquivo", value=True)
        
        nome_arquivo_saida = None
        if salvar_arquivo:
            nome_base = Path(arquivo_audio.name).stem
            nome_arquivo_saida = st.text_input(
                "Nome do arquivo de saída (.txt)",
                value=f"{nome_base}_transcricao.txt",
                help="Nome do arquivo onde a transcrição será salva"
            )
        
        # Botão de processar
        processar = st.button("🚀 Transcrever Áudio", type="primary", use_container_width=True)
        
        if processar:
            if not nome_arquivo_saida and salvar_arquivo:
                st.error("⚠️ Por favor, informe o nome do arquivo de saída ou desmarque a opção de salvar.")
            else:
                # Cria arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(arquivo_audio.name).suffix) as tmp_file:
                    tmp_file.write(arquivo_audio.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Barra de progresso
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.info("⏳ Carregando modelo Whisper... Isso pode levar alguns segundos na primeira vez.")
                    progress_bar.progress(10)
                    
                    # Inicializa transcritor
                    try:
                        transcritor = TranscritorAudio(modelo=modelo)
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar modelo: {str(e)}")
                        st.info("💡 Dica: Tente usar um modelo menor (tiny ou base) se o problema persistir.")
                        st.stop()
                    progress_bar.progress(30)
                    
                    status_text.info("🎙️ Transcrevendo áudio... Isso pode levar alguns minutos dependendo do tamanho do arquivo.")
                    progress_bar.progress(50)
                    
                    # Transcreve
                    texto = transcritor.transcrever(
                        arquivo_audio=tmp_path,
                        idioma=idioma,
                        salvar_arquivo=nome_arquivo_saida if salvar_arquivo else None
                    )
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Mostra resultado
                    st.success("✅ Transcrição concluída com sucesso!")
                    
                    # Exibe texto transcrito
                    st.header("📝 Transcrição")
                    st.text_area(
                        "Texto transcrito:",
                        value=texto,
                        height=300,
                        help="Você pode copiar este texto"
                    )
                    
                    # Botão de download se salvou arquivo
                    if salvar_arquivo and nome_arquivo_saida:
                        if os.path.exists(nome_arquivo_saida):
                            with open(nome_arquivo_saida, 'r', encoding='utf-8') as f:
                                arquivo_txt = f.read()
                            
                            st.download_button(
                                label="📥 Baixar Transcrição (.txt)",
                                data=arquivo_txt,
                                file_name=nome_arquivo_saida,
                                mime="text/plain",
                                use_container_width=True
                            )
                    
                    # Estatísticas
                    palavras = len(texto.split())
                    caracteres = len(texto)
                    
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("📊 Palavras", palavras)
                    with col_stat2:
                        st.metric("🔤 Caracteres", caracteres)
                    with col_stat3:
                        st.metric("⏱️ Modelo", modelo_selecionado)
                    
                except FileNotFoundError as e:
                    if "ffmpeg" in str(e).lower():
                        st.error("""
                        ❌ **Erro: FFmpeg necessário para este formato de áudio.**
                        
                        O Whisper precisa do FFmpeg para processar este tipo de arquivo.
                        No Streamlit Cloud, o FFmpeg deveria estar disponível.
                        
                        **Soluções:**
                        1. Tente um formato diferente (MP3 ou WAV geralmente funcionam melhor)
                        2. Aguarde alguns segundos e tente novamente
                        3. Se o problema persistir, o Streamlit Cloud pode estar com problema temporário
                        """)
                    else:
                        st.error(f"❌ Arquivo não encontrado: {str(e)}")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "ffmpeg" in error_msg or "codec" in error_msg:
                        st.error("""
                        ❌ **Erro ao processar áudio.**
                        
                        Isso pode ser causado por:
                        - Formato de áudio não suportado
                        - FFmpeg não disponível
                        - Arquivo corrompido
                        
                        **Tente:**
                        - Converter o áudio para MP3 ou WAV
                        - Usar um arquivo menor
                        - Tentar novamente em alguns segundos
                        """)
                    else:
                        st.error(f"❌ Erro ao processar: {str(e)}")
                    st.exception(e)
                finally:
                    # Remove arquivo temporário
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

with col2:
    st.header("ℹ️ Como Usar")
    st.markdown("""
    1. **Selecione o modelo** na barra lateral
    2. **Escolha o idioma** do áudio
    3. **Faça upload** do arquivo de áudio
    4. **Configure** se deseja salvar o arquivo
    5. **Clique em Transcrever** e aguarde
    
    ⚠️ **Atenção:** O processamento pode levar alguns minutos dependendo do tamanho do áudio e do modelo escolhido.
    """)
    
    st.markdown("---")
    
    st.header("💡 Dicas")
    st.markdown("""
    - Use o modelo **Base** para um bom equilíbrio entre velocidade e precisão
    - Modelos maiores são mais precisos mas demoram muito mais
    - A detecção automática de idioma funciona bem na maioria dos casos
    - Arquivos menores processam mais rápido
    """)

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Desenvolvido por Cristiano Lino usando OpenAI Whisper e Streamlit"
    "</div>",
    unsafe_allow_html=True
)

