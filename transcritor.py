#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transcritor de Áudio para Texto
Ferramenta simples para transcrever áudios em diversos formatos e buscar palavras
"""

import os
import sys
import argparse
import re
from pathlib import Path

# Atualiza PATH no Windows para incluir variáveis de ambiente do sistema
# Isso garante que o FFmpeg seja encontrado mesmo após instalação recente
if sys.platform == "win32":
    try:
        import winreg
        
        # Obtém PATH do registro do Windows (sistema e usuário)
        machine_path = ""
        user_path = ""
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                machine_path = winreg.QueryValueEx(key, "Path")[0]
        except:
            pass
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                              r"Environment") as key:
                user_path = winreg.QueryValueEx(key, "Path")[0]
        except:
            pass
        
        # Atualiza PATH do processo atual combinando ambos
        current_path = os.environ.get("Path", "")
        if machine_path:
            if current_path and machine_path not in current_path:
                os.environ["Path"] = f"{machine_path};{current_path}"
            elif not current_path:
                os.environ["Path"] = machine_path
        
        if user_path:
            current_path = os.environ.get("Path", "")
            if current_path and user_path not in current_path:
                os.environ["Path"] = f"{user_path};{current_path}"
            elif not current_path:
                os.environ["Path"] = user_path
                
    except Exception:
        # Se falhar, continua normalmente
        pass

try:
    import whisper
except ImportError:
    print("ERRO: Biblioteca whisper não instalada!")
    print("Execute: pip install -r requirements.txt")
    sys.exit(1)

# Verifica se FFmpeg está disponível antes de usar
def verificar_ffmpeg():
    """Verifica se o FFmpeg está disponível no sistema"""
    import shutil
    return shutil.which("ffmpeg") is not None

if not verificar_ffmpeg():
    print("\n" + "="*60)
    print("ERRO: FFmpeg não encontrado!")
    print("="*60)
    print("O FFmpeg é necessário para processar arquivos de áudio.")
    print("\nPara instalar no Windows:")
    print("  1. Execute: winget install --id=Gyan.FFmpeg -e")
    print("  2. Feche e reabra este terminal")
    print("\nOu baixe manualmente em: https://ffmpeg.org/download.html")
    print("="*60)
    sys.exit(1)

# Tenta importar pydub, mas não é obrigatório (Python 3.13 pode ter problemas)
try:
    from pydub import AudioSegment
    PYDUB_DISPONIVEL = True
except ImportError:
    PYDUB_DISPONIVEL = False
    print("AVISO: pydub não disponível. Alguns formatos podem não funcionar.")
    print("O Whisper tentará processar o arquivo diretamente.")


class TranscritorAudio:
    """Classe principal para transcrição de áudio"""
    
    def __init__(self, modelo="base"):
        """
        Inicializa o transcritor
        
        Args:
            modelo: Tamanho do modelo Whisper ('tiny', 'base', 'small', 'medium', 'large')
        """
        print(f"Carregando modelo Whisper '{modelo}'...")
        self.modelo = whisper.load_model(modelo)
        print("Modelo carregado com sucesso!")
    
    def converter_audio(self, arquivo_entrada, arquivo_saida=None):
        """
        Converte áudio para formato WAV (necessário para o Whisper)
        
        Args:
            arquivo_entrada: Caminho do arquivo de áudio original
            arquivo_saida: Caminho do arquivo WAV de saída (opcional)
        """
        if not PYDUB_DISPONIVEL:
            # Se pydub não estiver disponível, tenta usar o arquivo diretamente
            # O Whisper suporta vários formatos nativamente
            print("AVISO: pydub não disponível. Tentando processar arquivo diretamente.")
            return arquivo_entrada
        
        if arquivo_saida is None:
            arquivo_saida = str(Path(arquivo_entrada).with_suffix('.wav'))
        
        print(f"Convertendo {arquivo_entrada} para WAV...")
        
        # Detecta formato pelo extensão
        formato = Path(arquivo_entrada).suffix[1:].lower()
        
        try:
            audio = AudioSegment.from_file(arquivo_entrada, format=formato)
            # Converte para mono, 16kHz (ideal para Whisper)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(arquivo_saida, format="wav")
            print(f"Conversão concluída: {arquivo_saida}")
            return arquivo_saida
        except Exception as e:
            print(f"ERRO na conversão: {e}")
            # Se falhar, tenta usar o arquivo original
            return arquivo_entrada
    
    def transcrever(self, arquivo_audio, idioma="pt", salvar_arquivo=None):
        """
        Transcreve arquivo de áudio para texto
        
        Args:
            arquivo_audio: Caminho do arquivo de áudio
            idioma: Código do idioma ('pt', 'en', 'es', etc.) ou None para detecção automática
            salvar_arquivo: Caminho para salvar a transcrição em arquivo .txt (opcional)
        
        Returns:
            str: Texto transcrito
        """
        if not os.path.exists(arquivo_audio):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_audio}")
        
        print(f"\nTranscrevendo: {arquivo_audio}")
        print("Isso pode levar alguns minutos dependendo do tamanho do áudio...")
        
        # Converte para WAV se necessário e se pydub estiver disponível
        # O Whisper suporta MP3, WAV, M4A e outros formatos diretamente
        extensao = Path(arquivo_audio).suffix.lower()
        formatos_suportados_diretamente = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
        if extensao not in formatos_suportados_diretamente and PYDUB_DISPONIVEL:
            arquivo_audio = self.converter_audio(arquivo_audio)
        
        # Transcreve
        resultado = self.modelo.transcribe(
            arquivo_audio,
            language=idioma if idioma else None,
            task="transcribe"
        )
        
        texto = resultado["text"].strip()
        
        # Salva em arquivo se solicitado
        if salvar_arquivo:
            with open(salvar_arquivo, 'w', encoding='utf-8') as f:
                f.write(texto)
            print(f"\nTranscrição salva em: {salvar_arquivo}")
        
        return texto
    
    def buscar_palavras(self, texto, palavras_busca, case_sensitive=False):
        """
        Busca palavras ou frases no texto transcrito
        
        Args:
            texto: Texto onde buscar
            palavras_busca: Lista de palavras/frases para buscar ou string única
            case_sensitive: Se True, diferencia maiúsculas/minúsculas
        
        Returns:
            dict: Dicionário com resultados da busca
        """
        if isinstance(palavras_busca, str):
            palavras_busca = [palavras_busca]
        
        resultados = {}
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for palavra in palavras_busca:
            padrao = re.escape(palavra)  # Escapa caracteres especiais
            matches = list(re.finditer(padrao, texto, flags))
            
            resultados[palavra] = {
                'ocorrencias': len(matches),
                'posicoes': [match.start() for match in matches],
                'contextos': []
            }
            
            # Adiciona contexto (50 caracteres antes e depois)
            for match in matches:
                inicio = max(0, match.start() - 50)
                fim = min(len(texto), match.end() + 50)
                contexto = texto[inicio:fim].replace('\n', ' ')
                resultados[palavra]['contextos'].append(contexto)
        
        return resultados
    
    def transcrever_e_buscar(self, arquivo_audio, palavras_busca=None, idioma="pt", 
                            salvar_transcricao=None, case_sensitive=False):
        """
        Transcreve áudio e busca palavras em uma única operação
        
        Args:
            arquivo_audio: Caminho do arquivo de áudio
            palavras_busca: Lista de palavras para buscar (opcional)
            idioma: Código do idioma
            salvar_transcricao: Caminho para salvar transcrição (opcional)
            case_sensitive: Se True, diferencia maiúsculas/minúsculas na busca
        
        Returns:
            tuple: (texto_transcrito, resultados_busca)
        """
        # Transcreve
        texto = self.transcrever(arquivo_audio, idioma, salvar_transcricao)
        
        # Busca palavras se fornecidas
        resultados_busca = None
        if palavras_busca:
            print(f"\nBuscando palavras: {', '.join(palavras_busca)}")
            resultados_busca = self.buscar_palavras(texto, palavras_busca, case_sensitive)
            
            # Exibe resultados
            print("\n" + "="*60)
            print("RESULTADOS DA BUSCA:")
            print("="*60)
            for palavra, dados in resultados_busca.items():
                print(f"\nPalavra: '{palavra}'")
                print(f"  Ocorrências encontradas: {dados['ocorrencias']}")
                if dados['ocorrencias'] > 0:
                    print(f"  Posições no texto: {dados['posicoes']}")
                    print("\n  Contextos:")
                    for i, contexto in enumerate(dados['contextos'][:5], 1):  # Mostra até 5 contextos
                        print(f"    {i}. ...{contexto}...")
                    if len(dados['contextos']) > 5:
                        print(f"    ... e mais {len(dados['contextos']) - 5} ocorrência(s)")
        
        return texto, resultados_busca


def main():
    """Função principal com interface de linha de comando"""
    parser = argparse.ArgumentParser(
        description="Transcritor de Áudio para Texto com Busca",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Transcrever apenas:
  python transcritor.py audio.mp3
  
  # Transcrever e salvar:
  python transcritor.py audio.mp3 -o transcricao.txt
  
  # Transcrever e buscar palavras:
  python transcritor.py audio.mp3 -b "palavra1" "palavra2"
  
  # Usar modelo maior (mais preciso, mais lento):
  python transcritor.py audio.mp3 -m medium
  
  # Busca case-sensitive:
  python transcritor.py audio.mp3 -b "Python" -c
        """
    )
    
    parser.add_argument('arquivo', nargs='?', help='Caminho do arquivo de áudio a transcrever')
    parser.add_argument('-o', '--output', help='Arquivo para salvar a transcrição (.txt)')
    parser.add_argument('-b', '--buscar', nargs='+', help='Palavras ou frases para buscar no texto')
    parser.add_argument('-m', '--modelo', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Modelo Whisper a usar (padrão: base)')
    parser.add_argument('-i', '--idioma', default='pt',
                       help='Código do idioma (pt, en, es, etc.) ou "auto" para detecção automática')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                       help='Busca diferencia maiúsculas/minúsculas')
    
    args = parser.parse_args()
    
    # Se não forneceu arquivo, mostra ajuda
    if args.arquivo is None:
        parser.print_help()
        sys.exit(1)
    
    # Valida arquivo
    if not os.path.exists(args.arquivo):
        print(f"ERRO: Arquivo não encontrado: {args.arquivo}")
        sys.exit(1)
    
    # Processa idioma
    idioma = None if args.idioma.lower() == 'auto' else args.idioma
    
    try:
        # Inicializa transcritor
        transcritor = TranscritorAudio(modelo=args.modelo)
        
        # Executa transcrição e busca
        texto, resultados = transcritor.transcrever_e_buscar(
            arquivo_audio=args.arquivo,
            palavras_busca=args.buscar,
            idioma=idioma,
            salvar_transcricao=args.output,
            case_sensitive=args.case_sensitive
        )
        
        # Exibe transcrição
        print("\n" + "="*60)
        print("TRANSCRIÇÃO COMPLETA:")
        print("="*60)
        print(texto)
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

