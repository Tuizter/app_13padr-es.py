# app_13padrões.py
import streamlit as st
from collections import Counter

# --- CLASSE PRINCIPAL: O CÉREBRO DO ANALISADOR ---
class RoletaMestre:
    def __init__(self):
        # --- DADOS ESTRUTURAIS DA ROLETA ---
        self.CILINDRO_EUROPEU = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        
        # --- MAPEAMENTOS PRÉ-CALCULADOS PARA EFICIÊNCIA ---
        self.NUMERO_INFO = self._mapear_info_numeros()
        self.VIZINHOS_MAPEADOS = self._mapear_vizinhos_do_cilindro()
        self.TERMINAIS_MAPEADOS = self._mapear_terminais()
        self.REGIOES_TERMINAIS = self._calcular_regioes_dos_terminais()
        self.CAVALOS_LATERAIS_PARA_CENTRAL = self._mapear_cavalos_laterais()

        # --- ESTADO DINÂMICO DA ANÁLISE ---
        self.historico = []
        self.tendencia_atual = None
        self.modo_retorno = None
        self.modo_espera_quebra = None # NOVO: Para padrões que precisam de uma quebra

    # --- MÉTODOS DE INICIALIZAÇÃO E MAPEAMENTO ---
    def _mapear_info_numeros(self):
        info = {}
        voisins = {0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35}
        tiers = {5, 8, 10, 11, 13, 16, 23, 24, 27, 30, 33, 36}
        orphelins = {1, 6, 9, 14, 17, 20, 31, 34}
        for num in range(37):
            secao = "Voisins" if num in voisins else "Tiers" if num in tiers else "Orphelins"
            info[num] = {
                'terminal': num % 10,
                'duzia': 1 if 1 <= num <= 12 else 2 if 13 <= num <= 24 else 3 if 25 <= num <= 36 else 0,
                'dezena': (num // 10) * 10 if num > 0 else 0,
                'secao': secao
            }
        return info

    def _mapear_vizinhos_do_cilindro(self):
        vizinhos = {}
        tamanho = len(self.CILINDRO_EUROPEU)
        for i, num in enumerate(self.CILINDRO_EUROPEU):
            vizinhos[num] = {
                "v-3": self.CILINDRO_EUROPEU[(i - 3 + tamanho) % tamanho],
                "v-2": self.CILINDRO_EUROPEU[(i - 2 + tamanho) % tamanho],
                "v-1": self.CILINDRO_EUROPEU[(i - 1 + tamanho) % tamanho],
                "num": num,
                "v+1": self.CILINDRO_EUROPEU[(i + 1) % tamanho],
                "v+2": self.CILINDRO_EUROPEU[(i + 2) % tamanho],
                "v+3": self.CILINDRO_EUROPEU[(i + 3) % tamanho],
            }
        return vizinhos

    def _mapear_terminais(self):
        terminais = {i: [] for i in range(10)}
        for i in range(37):
            terminais[i % 10].append(i)
        return terminais

    def _calcular_regioes_dos_terminais(self):
        regioes = {}
        for terminal, numeros_do_terminal in self.TERMINAIS_MAPEADOS.items():
            regiao_completa = set()
            for num in numeros_do_terminal:
                v = self.VIZINHOS_MAPEADOS[num]
                regiao_completa.update([v['v-2'], v['v-1'], v['num'], v['v+1'], v['v+2']])
            regioes[terminal] = sorted(list(regiao_completa))
        return regioes

    def _mapear_cavalos_laterais(self):
        mapa = {}
        cavalos_triplos = {0:[3,7], 1:[4,8], 2:[5,9], 3:[6,0], 4:[7,1], 5:[8,1], 6:[9,2], 7:[0,4]} # Adicionei mais para cobrir todos os padrões
        for central, laterais in cavalos_triplos.items():
            chave = tuple(sorted(laterais))
            mapa[chave] = central
        return mapa
    
    # --- MÉTODOS PÚBLICOS ---
    def adicionar_numero(self, numero):
        if 0 <= numero <= 36:
            self.historico.append(numero)
            if len(self.historico) > 20:
                self.historico.pop(0)
            # Reseta modos de espera se um novo número chega
            self.modo_espera_quebra = None

    # --- LÓGICA DE ANÁLISE EM CAMADAS ---
    def _gerenciar_ciclo_vida(self):
        if self.tendencia_atual:
            # Lógica de Quebra
            pass # Simplificado para focar nas novas estratégias
        if self.modo_retorno:
            # Lógica de Retorno
            pass # Simplificado
        return None

    def _calcular_valor_falso(self, num):
        if num >= 10:
            return (num // 10 + num % 10) % 10
        return None

    def _analisar_ondas(self):
        if len(self.historico) < 3: return None
        h = self.historico
        terminais_h = [self.NUMERO_INFO[n]['terminal'] for n in h]

        # --- IMPLEMENTAÇÃO DAS ESTRATÉGIAS 2.0 ---

        # Padrão Falso -> Verdadeiro
        vf_penultimo = self._calcular_valor_falso(h[-2])
        vt_ultimo = terminais_h[-1]
        if vf_penultimo is not None and vf_penultimo == vt_ultimo:
            vf_ultimo = self._calcular_valor_falso(h[-1])
            if vf_ultimo is not None:
                return {"diagnostico": f"**Gatilho Falso/Verdadeiro!** O padrão `Falso -> Verdadeiro` está ativo. O número {h[-1]} é um Terminal {vf_ultimo} Falso.",
                        "estrategia": f"Apostar na região do **Terminal {vf_ultimo} Verdadeiro**.",
                        "numeros_recomendados": self.REGIOES_TERMINAIS[vf_ultimo]}

        # Padrão Vai e Vem (A -> B -> A)
        secao_a, secao_b, secao_c = self.NUMERO_INFO[h[-3]]['secao'], self.NUMERO_INFO[h[-2]]['secao'], self.NUMERO_INFO[h[-1]]['secao']
        if secao_a == secao_c and secao_a != secao_b:
            return {"diagnostico": f"**Gatilho Vai e Vem!** Alternância entre {secao_a} e {secao_b}.",
                    "estrategia": f"Apostar na região do número {h[-2]}, buscando o retorno para a seção {secao_b}.",
                    "numeros_recomendados": list(self.VIZINHOS_MAPEADOS[h[-2]].values())}
        
        # Padrão Dobra/Metade
        for i in range(len(h) - 2, 0, -1):
            if h[i+1] == h[i] * 2 or h[i+1] == h[i] // 2: # Gatilho
                dobra = h[-1] * 2
                metade = h[-1] // 2
                alvos = []
                if 0 <= dobra <= 36: alvos.append(dobra)
                if 0 <= metade <= 36: alvos.append(metade)
                if alvos:
                    return {"diagnostico": f"**Gatilho de Dobra/Metade Ativado!** (Padrão visto: {h[i]} -> {h[i+1]})",
                            "estrategia": f"Analisando o último número ({h[-1]}). Apostar na região dos alvos de dobra/metade: {', '.join(map(str, alvos))}.",
                            "numeros_recomendados": list(self.VIZINHOS_MAPEADOS[alvos[0]].values())}
                break

        # Padrões de Cavalo com Quebra (0, 1, 2, 3, 7, 8, 9)
        par_terminais = tuple(sorted(terminais_h[-3:-1]))
        if par_terminais in self.CAVALOS_LATERAIS_PARA_CENTRAL:
            central_alvo = self.CAVALOS_LATERAIS_PARA_CENTRAL[par_terminais]
            trindade = set(list(par_terminais) + [central_alvo])
            if terminais_h[-1] not in trindade: # Confirma que o último número foi uma quebra
                return {"diagnostico": f"**Padrão de Cavalo com Quebra!** O par {par_terminais} foi seguido pela quebra {h[-1]}.",
                        "estrategia": f"Apostar na região do **Terminal {central_alvo}** por 2 a 3 rodadas.",
                        "numeros_recomendados": self.REGIOES_TERMINAIS[central_alvo]}

        return None

    def _identificar_mares(self):
        # Lógica de marés (tendências de fundo) como antes
        pass # Simplificado para focar nas novas estratégias
    
    def analisar(self):
        if len(self.historico) < 3:
            return {"diagnostico": "Aguardando mais números...", "estrategia": "Insira pelo menos 3 números para iniciar a análise."}

        # --- NOVA ORQUESTRAÇÃO ---
        # 1. Prioridade para Ondas (gatilhos rápidos 2.0)
        resultado_ondas = self._analisar_ondas()
        if resultado_ondas:
            return resultado_ondas
            
        # 2. Se nenhuma onda for detectada, procurar por marés (padrões antigos)
        # resultado_mares = self._identificar_mares()
        # if resultado_mares:
        #     return resultado_mares
            
        return {"diagnostico": "Nenhum padrão claro identificado.", "estrategia": "Aguardar a formação de uma tendência ou um gatilho."}


# --- INTERFACE DO APLICATIVO (STREAMLIT) ---

st.set_page_config(layout="wide", page_title="Roleta Mestre")
st.title("Roleta Mestre 🎲 2.0")
st.markdown("Analisador de estratégias e manipulações em tempo real.")

if 'analista' not in st.session_state:
    st.session_state.analista = RoletaMestre()

st.header("Clique no número sorteado para adicionar ao histórico:")

# Tabela de Roleta Interativa
col_zero, col_table = st.columns([1, 12])
if col_zero.button("0", key="num_0", use_container_width=True):
    st.session_state.analista.adicionar_numero(0)
    st.rerun()

with col_table:
    numeros = [[3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
               [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
               [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]]
    cols = st.columns(12)
    for i in range(12):
        for j in range(3):
            num = numeros[j][i]
            if cols[i].button(f"{num}", key=f"num_{num}", use_container_width=True):
                st.session_state.analista.adicionar_numero(num)
                st.rerun()

st.divider()
st.header("Painel de Análise")

historico_atual = st.session_state.analista.historico
if historico_atual:
    st.metric("Último Número Adicionado", historico_atual[-1])
historico_str = ", ".join(map(str, historico_atual))
st.write(f"**Histórico Analisado ({len(historico_atual)}/20):** `{historico_str or 'Vazio'}`")

resultado_analise = st.session_state.analista.analisar()
if resultado_analise:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Diagnóstico:")
        st.info(resultado_analise.get('diagnostico', ''))
    with col2:
        st.subheader("Estratégia Recomendada:")
        st.success(resultado_analise.get('estrategia', ''))
        
        numeros_rec = resultado_analise.get('numeros_recomendados')
        if numeros_rec:
            with st.expander(f"Ver os {len(numeros_rec)} números recomendados"):
                numeros_formatados = ' - '.join(map(str, numeros_rec))
                st.code(numeros_formatados, language=None)

with st.sidebar:
    st.header("Controles")
    if st.button("Limpar Histórico e Reiniciar"):
        st.session_state.analista = RoletaMestre()
        st.rerun()
    st.markdown("---")
    st.subheader("Lembre-se:")
    st.warning("Este é um analisador de padrões e não garante vitórias. Jogue com responsabilidade.")