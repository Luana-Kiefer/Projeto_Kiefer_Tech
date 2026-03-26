import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# ARQUIVOS ONDE TUDO FICA SALVO 
ARQUIVO_VENDAS = "vendas_loja.csv"
ARQUIVO_ESTOQUE = "estoque_loja.csv"
ARQUIVO_ENCOMENDAS = "encomendas_loja.csv"

# Funçãozinha pra ler os dados e não dar erro se o arquivo sumir
def carregar_dados(arquivo, colunas):
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo)
            for col in colunas:
                if col not in df.columns:
                    df[col] = ""
            return df[colunas]
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

# DEIXANDO O SITE BONITÃO - AJUSTE DE ESPAÇO E CORES
st.set_page_config(page_title="Kiefer Tech - Gestão Integrada", layout="wide")

st.markdown("""
    <style>
    /* REMOVER ESPAÇO VAZIO NO TOPO */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    /* Linha azul embaixo da aba quando clica */
    div[data-baseweb="tab-highlight"] {
        background-color: #60a5fa !important;
    }
    
    /* Cor do texto da aba selecionada */
    button[aria-selected="true"] p {
        color: #60a5fa !important;
    }

    /* Quando passa o mouse nas abas */
    button[data-baseweb="tab"]:hover p {
        color: #93c5fd !important;
    }

    /* Remover contornos de foco */
    button[data-baseweb="tab"]:focus {
        outline: none !important;
    }
    
    /* Tamanho das letras pra enxergar de longe no balcão */
    button[data-baseweb="tab"] p {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    h1 { font-size: 44px !important; margin-top: 0px !important; }
    h2 { font-size: 34px !important; }
    .stMarkdown p, label { font-size: 20px !important; font-weight: 500 !important; }
    
    /* Botão Principal de Transação - azulão */
    .stButton>button { 
        width: 100%; 
        border-radius: 6px; 
        height: 4em; 
        background-color: #1e3a8a; 
        color: white; 
        font-size: 22px !important;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #1e40af; }

    /* Estilo do cabeçalho centralizado */
    .main-header {
        text-align: center;
        padding-top: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO PRINCIPAL E LOGO
st.markdown("<div class='main-header'>", unsafe_allow_html=True)

# Lógica da Logo - Tenta carregar se o arquivo logo.png estiver no GitHub
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=150)

st.title("Sistema de Gestão de Vendas")
st.write(f"Operação: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# ABAS DO SISTEMA
aba_vendas, aba_estoque, aba_encomendas = st.tabs([
    "Frente de Caixa", 
    "Gestão de Estoque", 
    "Encomendas Especializadas"
])

# PARTE DO ESTOQUE
with aba_estoque:
    st.header("Administração de Inventário")
    df_estoque = carregar_dados(ARQUIVO_ESTOQUE, ['Produto', 'Quantidade'])
    
    with st.form("form_estoque", clear_on_submit=True):
        col_e1, col_e2 = st.columns(2)
        novo_p = col_e1.text_input("Descrição do Produto", placeholder="Ex: iPhone 13 128GB")
        qtd_p = col_e2.number_input("Quantidade em Unidades", min_value=0, step=1)
        btn_estoque = st.form_submit_button("ATUALIZAR INVENTÁRIO")
        
        if btn_estoque and novo_p:
            if novo_p in df_estoque['Produto'].values:
                df_estoque.loc[df_estoque['Produto'] == novo_p, 'Quantidade'] = qtd_p
            else:
                novo_item = pd.DataFrame([{'Produto': novo_p, 'Quantidade': qtd_p}])
                df_estoque = pd.concat([df_estoque, novo_item], ignore_index=True)
            df_estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
            st.success(f"Registro de '{novo_p}' atualizado.")
            st.rerun()

    st.write("### Relatório de Posição de Estoque")
    st.dataframe(df_estoque, use_container_width=True)

# PARTE DAS ENCOMENDAS - PRA NÃO ESQUECER PEDIDO
with aba_encomendas:
    st.header("Gestão de Pedidos e Encomendas")
    colunas_enc = ['Data', 'Cliente', 'WhatsApp', 'Item Solicitado', 'Valor da Transação', 'Status']
    df_enc = carregar_dados(ARQUIVO_ENCOMENDAS, colunas_enc)
    
    with st.form("form_encomenda", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome_c = c1.text_input("Nome do Cliente")
        whats_c = c2.text_input("WhatsApp de Contato")
        item_c = st.text_input("Item Encomendado")
        c3, c4 = st.columns(2)
        valor_enc = c3.number_input("Valor da Transação em Reais", value=None, placeholder="0,00", step=0.01)
        status_c = c4.selectbox("Como tá o pedido?", ["Pendente (Comprar)", "Comprado (Aguardando)", "Disponível (Avisar Cliente)"])
        
        if st.form_submit_button("REGISTRAR ENCOMENDA"):
            if nome_c and item_c and valor_enc is not None:
                nova_enc = {
                    'Data': datetime.now().strftime("%d/%m/%Y"), 'Cliente': nome_c,
                    'WhatsApp': whats_c, 'Item Solicitado': item_c,
                    'Valor da Transação': valor_enc, 'Status': status_c
                }
                df_enc = pd.concat([df_enc, pd.DataFrame([nova_enc])], ignore_index=True)
                df_enc.to_csv(ARQUIVO_ENCOMENDAS, index=False)
                st.success("Encomenda registrada com sucesso.")
                st.rerun()
            else:
                st.error("Preencha o nome, item e valor da transação.")

    st.write("### Lista de Encomendas Ativas")
    st.dataframe(df_enc, use_container_width=True)

# PARTE DAS VENDAS - O CAIXA
with aba_vendas:
    st.header("Painel de Lançamento de Vendas")
    colunas_vendas = ['Data', 'Hora', 'Cliente', 'Produto', 'Categoria', 'Valor (R$)', 'Pagamento', 'Observações']
    df_vendas = carregar_dados(ARQUIVO_VENDAS, colunas_vendas)
    
    col_v1, col_v2 = st.columns([1, 1.6])
    
    with col_v1:
        # Pega a lista de produtos que cadastramos no estoque
        lista_produtos = df_estoque['Produto'].tolist() if not df_estoque.empty else []
        produto_selecionado = st.selectbox("Escolha o item vendido", lista_produtos if lista_produtos else ["Nenhum item em estoque"])
        
        # Aviso se o estoque estiver acabando - fica vermelho
        if not df_estoque.empty and produto_selecionado in df_estoque['Produto'].values:
            qtd_atual = df_estoque.loc[df_estoque['Produto'] == produto_selecionado, 'Quantidade'].values[0]
            if 0 < qtd_atual <= 2:
                st.error(f"Olha o estoque! Só tem {qtd_atual} unidades de '{produto_selecionado}'.")
            elif qtd_atual == 0:
                st.error(f"Acabou! '{produto_selecionado}' tá zerado no estoque.")

        with st.form("form_venda", clear_on_submit=True):
            cliente_venda = st.text_input("Identificação do Cliente - Nome ou CPF")
            obs_venda = st.text_area("Observações da Venda")
            
            # Categoria com eletrodomésticos corrigido
            cat_prod = st.selectbox("O que é?", [
                "periféricos", "acessorios", "celulares", 
                "peças de hardware", "eletrodomésticos", "serviços e manutenção"
            ])
            
            valor_venda = st.number_input("Valor final da venda", value=None, placeholder="0,00", step=0.01)
            forma_pgto = st.radio("Forma de pagamento", ["Pix", "Cartão", "Boleto", "Dinheiro"], horizontal=True)
            
            if st.form_submit_button("REGISTRAR TRANSAÇÃO"):
                if lista_produtos and valor_venda is not None and valor_venda > 0:
                    qtd_disponivel = df_estoque.loc[df_estoque['Produto'] == produto_selecionado, 'Quantidade'].values[0]
                    eh_servico = cat_prod == "serviços e manutenção"
                    
                    if eh_servico or qtd_disponivel > 0:
                        if not eh_servico:
                            # Tira do estoque se não for serviço
                            df_estoque.loc[df_estoque['Produto'] == produto_selecionado, 'Quantidade'] = qtd_disponivel - 1
                            df_estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
                        
                        # Salva a venda no arquivo
                        nova_v = {
                            'Data': datetime.now().strftime("%d/%m/%Y"), 'Hora': datetime.now().strftime("%H:%M:%S"),
                            'Cliente': cliente_venda, 'Produto': produto_selecionado, 'Categoria': cat_prod, 
                            'Valor (R$)': valor_venda, 'Pagamento': forma_pgto, 'Observações': obs_venda
                        }
                        df_vendas = pd.concat([df_vendas, pd.DataFrame([nova_v])], ignore_index=True)
                        df_vendas.to_csv(ARQUIVO_VENDAS, index=False)
                        st.success("Venda registrada com sucesso.")
                        st.rerun()
                    else:
                        st.error("Não dá pra vender, tá sem estoque.")
                else:
                    st.error("Verifica o produto e o valor da venda.")

    with col_v2:
        # Gráficos e totais pra acompanhar o dinheiro
        st.subheader("Indicadores de Faturamento")
        if not df_vendas.empty:
            # Filtro pra escolher o que quer analisar
            filtro = st.radio("Ver faturamento de:", ["Visualizar Hoje", "Visualizar por Mês"], horizontal=True)
            
            if filtro == "Visualizar Hoje":
                hoje_str = datetime.now().strftime("%d/%m/%Y")
                df_filtrado = df_vendas[df_vendas['Data'] == hoje_str]
                rotulo = "Hoje"
            else:
                # Pega os meses disponíveis no arquivo pra mostrar no filtro
                df_vendas['Mes_Ano'] = df_vendas['Data'].apply(lambda x: x[3:])
                meses_lista = sorted(df_vendas['Mes_Ano'].unique().tolist(), reverse=True)
                mes_selecionado = st.selectbox("Escolha o Mês/Ano:", meses_lista)
                df_filtrado = df_vendas[df_vendas['Mes_Ano'] == mes_selecionado]
                rotulo = mes_selecionado

            st.metric(f"Total faturado ({rotulo})", f"R$ {df_filtrado['Valor (R$)'].sum():.2f}")
            fig = px.pie(df_filtrado, values='Valor (R$)', names='Categoria', hole=0.4, title=f"Divisão por categoria ({rotulo})")
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"**Últimos lançamentos ({rotulo})**")
            st.dataframe(df_filtrado.tail(10), use_container_width=True)
        else:
            st.info("Aguardando as primeiras vendas lançadas.")