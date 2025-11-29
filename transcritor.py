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


def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_interativo():
    """Menu interativo para usuários leigos"""
    limpar_tela()
    
    print("="*60)
    print("  🎤 TRANSCRITOR DE ÁUDIO - MENU INTERATIVO")
    print("="*60)
    print()
    print("Escolha uma opção:")
    print()
    print("  1 - Transcrever áudio (apenas exibir na tela)")
    print("  2 - Transcrever áudio e salvar em arquivo")
    print("  3 - Transcrever áudio e buscar palavras")
    print("  4 - Sair")
    print()
    print("="*60)
    
    while True:
        try:
            opcao = input("Digite o número da opção (1-4): ").strip()
            
            if opcao == '1':
                executar_transcricao_simples()
                break
            elif opcao == '2':
                executar_transcricao_com_salvamento()
                break
            elif opcao == '3':
                executar_transcricao_com_busca()
                break
            elif opcao == '4':
                print("\nAté logo! 👋")
                sys.exit(0)
            else:
                print("\n❌ Opção inválida! Digite um número entre 1 e 4.\n")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Erro: {e}\n")


def solicitar_arquivo_audio():
    """Solicita o caminho do arquivo de áudio"""
    while True:
        arquivo = input("\n📁 Informe o caminho/nome do arquivo de áudio: ").strip()
        
        # Remove aspas se o usuário colocar
        arquivo = arquivo.strip('"\'')
        
        if not arquivo:
            print("❌ Por favor, informe um arquivo.")
            continue
        
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo não encontrado: {arquivo}")
            print("   Verifique se o caminho está correto e tente novamente.")
            continuar = input("\n   Deseja tentar novamente? (s/n): ").strip().lower()
            if continuar != 's':
                return None
        else:
            return arquivo


def solicitar_arquivo_saida(arquivo_entrada=None):
    """Solicita o nome do arquivo de saída"""
    while True:
        if arquivo_entrada:
            nome_sugerido = Path(arquivo_entrada).stem + "_transcricao.txt"
            print(f"\n💾 Nome sugerido: {nome_sugerido}")
            arquivo_saida = input("   Informe o nome do arquivo de saída (ou Enter para usar o sugerido): ").strip()
            
            if not arquivo_saida:
                arquivo_saida = nome_sugerido
        else:
            arquivo_saida = input("\n💾 Informe o nome do arquivo de saída (.txt): ").strip()
        
        # Remove aspas se o usuário colocar
        arquivo_saida = arquivo_saida.strip('"\'')
        
        if not arquivo_saida:
            print("❌ Por favor, informe um nome de arquivo.")
            continue
        
        # Adiciona extensão .txt se não tiver
        if not arquivo_saida.endswith('.txt'):
            arquivo_saida += '.txt'
        
        # Verifica se arquivo já existe
        if os.path.exists(arquivo_saida):
            sobrescrever = input(f"⚠️  O arquivo '{arquivo_saida}' já existe. Deseja sobrescrever? (s/n): ").strip().lower()
            if sobrescrever != 's':
                continue
        
        return arquivo_saida


def escolher_modelo():
    """Permite escolher o modelo Whisper"""
    print("\n" + "="*60)
    print("  Escolha o modelo Whisper:")
    print("="*60)
    print("  1 - tiny   (mais rápido, menos preciso)")
    print("  2 - base   (equilíbrio - RECOMENDADO)")
    print("  3 - small  (mais preciso, mais lento)")
    print("  4 - medium (muito preciso, bem lento)")
    print("  5 - large  (máxima precisão, muito lento)")
    print("="*60)
    
    modelos = {
        '1': 'tiny',
        '2': 'base',
        '3': 'small',
        '4': 'medium',
        '5': 'large'
    }
    
    while True:
        opcao = input("\nDigite o número da opção (1-5) ou Enter para usar 'base': ").strip()
        
        if not opcao:
            return 'base'
        
        if opcao in modelos:
            return modelos[opcao]
        else:
            print("❌ Opção inválida! Digite um número entre 1 e 5.")


def escolher_idioma():
    """Permite escolher o idioma"""
    print("\n" + "="*60)
    print("  Escolha o idioma:")
    print("="*60)
    print("  1 - Português (pt)")
    print("  2 - Inglês (en)")
    print("  3 - Espanhol (es)")
    print("  4 - Detecção automática")
    print("="*60)
    
    idiomas = {
        '1': 'pt',
        '2': 'en',
        '3': 'es',
        '4': None  # None = detecção automática
    }
    
    while True:
        opcao = input("\nDigite o número da opção (1-4) ou Enter para usar 'Português': ").strip()
        
        if not opcao:
            return 'pt'
        
        if opcao in idiomas:
            return idiomas[opcao]
        else:
            print("❌ Opção inválida! Digite um número entre 1 e 4.")


def executar_transcricao_simples():
    """Executa transcrição simples (apenas exibir)"""
    print("\n" + "="*60)
    print("  OPÇÃO 1: TRANSCREVER ÁUDIO")
    print("="*60)
    
    arquivo = solicitar_arquivo_audio()
    if not arquivo:
        return
    
    modelo = escolher_modelo()
    idioma = escolher_idioma()
    
    try:
        print("\n⏳ Inicializando transcritor...")
        transcritor = TranscritorAudio(modelo=modelo)
        
        texto = transcritor.transcrever(arquivo_audio=arquivo, idioma=idioma)
        
        print("\n" + "="*60)
        print("TRANSCRIÇÃO COMPLETA:")
        print("="*60)
        print(texto)
        print("="*60)
        
        input("\n\nPressione Enter para continuar...")
        
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        input("\n\nPressione Enter para continuar...")


def executar_transcricao_com_salvamento():
    """Executa transcrição e salva em arquivo"""
    print("\n" + "="*60)
    print("  OPÇÃO 2: TRANSCREVER E SALVAR")
    print("="*60)
    
    arquivo = solicitar_arquivo_audio()
    if not arquivo:
        return
    
    arquivo_saida = solicitar_arquivo_saida(arquivo)
    if not arquivo_saida:
        return
    
    modelo = escolher_modelo()
    idioma = escolher_idioma()
    
    try:
        print("\n⏳ Inicializando transcritor...")
        transcritor = TranscritorAudio(modelo=modelo)
        
        texto = transcritor.transcrever(
            arquivo_audio=arquivo,
            idioma=idioma,
            salvar_arquivo=arquivo_saida
        )
        
        print("\n" + "="*60)
        print("TRANSCRIÇÃO COMPLETA:")
        print("="*60)
        print(texto)
        print("="*60)
        print(f"\n✅ Transcrição salva em: {arquivo_saida}")
        
        input("\n\nPressione Enter para continuar...")
        
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        input("\n\nPressione Enter para continuar...")


def executar_transcricao_com_busca():
    """Executa transcrição e busca palavras"""
    print("\n" + "="*60)
    print("  OPÇÃO 3: TRANSCREVER E BUSCAR PALAVRAS")
    print("="*60)
    
    arquivo = solicitar_arquivo_audio()
    if not arquivo:
        return
    
    print("\n🔍 Informe as palavras ou frases que deseja buscar.")
    print("   (Você pode digitar várias palavras separadas por vírgula)")
    palavras_input = input("   Palavras para buscar: ").strip()
    
    if not palavras_input:
        print("❌ Nenhuma palavra informada. Operação cancelada.")
        return
    
    # Separa palavras por vírgula
    palavras_busca = [p.strip().strip('"\'') for p in palavras_input.split(',')]
    palavras_busca = [p for p in palavras_busca if p]  # Remove vazias
    
    if not palavras_busca:
        print("❌ Nenhuma palavra válida informada. Operação cancelada.")
        return
    
    salvar = input("\n💾 Deseja salvar a transcrição em arquivo? (s/n): ").strip().lower()
    arquivo_saida = None
    if salvar == 's':
        arquivo_saida = solicitar_arquivo_saida(arquivo)
        if not arquivo_saida:
            arquivo_saida = None
    
    modelo = escolher_modelo()
    idioma = escolher_idioma()
    
    try:
        print("\n⏳ Inicializando transcritor...")
        transcritor = TranscritorAudio(modelo=modelo)
        
        texto, resultados = transcritor.transcrever_e_buscar(
            arquivo_audio=arquivo,
            palavras_busca=palavras_busca,
            idioma=idioma,
            salvar_transcricao=arquivo_saida,
            case_sensitive=False
        )
        
        print("\n" + "="*60)
        print("TRANSCRIÇÃO COMPLETA:")
        print("="*60)
        print(texto)
        print("="*60)
        
        if arquivo_saida:
            print(f"\n✅ Transcrição salva em: {arquivo_saida}")
        
        input("\n\nPressione Enter para continuar...")
        
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        input("\n\nPressione Enter para continuar...")


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
  
  # Executar menu interativo (sem argumentos):
  python transcritor.py
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
    
    # Se não forneceu arquivo, mostra menu interativo
    if args.arquivo is None:
        menu_interativo()
        return
    
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

