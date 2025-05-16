import json
import os

class ComandosAdm:
    # Caminho do arquivo JSON
    arquivo_json = 'comandos/numerosParados.json'
    
    @staticmethod
    def ler_json():
        try:
            # Verifica se o arquivo existe antes de tentar abrir
            if not os.path.exists(ComandosAdm.arquivo_json):
                return []
            
            with open(ComandosAdm.arquivo_json, 'r') as file:
                dados = json.load(file)
                return dados
        except json.JSONDecodeError:
            print("Erro ao decodificar o arquivo JSON. Verifique o conteúdo do arquivo.")
            return []
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return []

    @staticmethod
    def escrever_json(dados):
        try:
            with open(ComandosAdm.arquivo_json, 'w') as file:
                json.dump(dados, file, indent=4)
        except Exception as e:
            print(f"Erro ao escrever no arquivo: {e}")

    @staticmethod
    def comandos(comando):
        try:
            numero = comando.split(' ', 1)[1]
            if comando.startswith("/stop"):
                dados = ComandosAdm.ler_json()
                if numero not in dados:
                    dados.append(numero)  # Adiciona o número à lista
                    ComandosAdm.escrever_json(dados)
                else:
                    print(f'O número {numero} já está na lista de bloqueados')

            elif comando.startswith("/start"):
                dados = ComandosAdm.ler_json()
                if numero in dados:
                    dados.remove(numero)  # Remove o número da lista
                    ComandosAdm.escrever_json(dados)
                else:
                    print(f'O número {numero} não está na lista de bloqueados')
        except Exception as e:
            print(f"Erro ao processar o comando: {e}")
    
    @staticmethod
    def verificar_numero_parado(numero):
        try:
            dados = ComandosAdm.ler_json()
            if numero in dados:
                return True
            else:
                return False
        except Exception as e:
            print(f"Erro ao verificar número parado: {e}")
            return False