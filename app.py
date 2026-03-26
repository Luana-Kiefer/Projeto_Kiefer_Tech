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

    /* 1. ABAS EM AZUL (CONFORME A FOTO) */
    div[data-baseweb="tab-highlight"] {
        background-color: #60a5fa !important;
    }
    button[aria-selected="true"] p {
        color: #60a5fa !important;
    }
    button[data-baseweb="tab"]:hover p {
        color: #93c5fd !important;
    }

    /* 2. ELEMENTOS EM VERMELHO - CONFORME A FOTO */
    div[data-baseweb="radio"] div[aria-checked="true"] {
        background-color: #ff4b4b !important;
    }
    
    /* Estilo do Botão Principal - Vermelho */
    .stButton>button { 
        width: 100%; 
        border-radius: 6px; 
        height: 4em; 
        background-color: #ff4b4b; 
        color: white; 
        font-size: 22px !important;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #ff6b6b; }

    /* Remover contornos de foco */
    button[data-baseweb="tab"]:focus {
        outline: none !important;
    }
    
    /* Tamanho das letras */
    button[data-baseweb="tab"] p {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    h1 { font-size: 44px !important; margin-top: 0px !important; }
    h2 { font-size: 34px !important; }
    .stMarkdown p, label { font-size: 20px !important; font-weight: 500 !important; }

    .main-header {
        text-align: center;
        padding-top: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO PRINCIPAL E LOGO
st.markdown("<div class='main-header'>", unsafe_allow_html=True)

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
    "Encomendas"
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

# PARTE DAS ENCOMENDAS
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
        valor_enc = c3.number_input("Valor da Transação (R$)", value=None, placeholder="0,00", step=0.01)
        status_c = c4.selectbox("Como tá o pedido?", ["Pendente (Comprar)", "Comprado (Aguardando)", "Disponível (Avisar Cliente)"])
        
        if st.form_submit_button("REGISTRAR ENCOMENDA"):
            if nome_c and item_c and valor_enc is not None:
                nova_enc = {'Data': datetime.now().strftime("%d/%m/%Y"), 'Cliente': nome_c, 'WhatsApp': whats_c, 'Item Solicitado': item_c, 'Valor da Transação': valor_enc, 'Status': status_c}
                pd.concat([df_enc, pd.DataFrame([nova_enc])], ignore_index=True).to_csv(ARQUIVO_ENCOMENDAS, index=False)
                st.success("Encomenda registrada.")
                st.rerun()

    st.dataframe(df_enc, use_container_width=True)

# PARTE DAS VENDAS - CAIXA
with aba_vendas:
    st.header("Painel de Lançamento de Vendas")
    df_vendas = carregar_dados(ARQUIVO_VENDAS, ['Data', 'Hora', 'Cliente', 'Produto', 'Categoria', 'Valor (R$)', 'Pagamento', 'Observações'])
    
    col_v1, col_v2 = st.columns([1, 1.6])
    
    with col_v1:
        lista_produtos = df_estoque['Produto'].tolist() if not df_estoque.empty else []
        produto_selecionado = st.selectbox("Item Selecionado", lista_produtos if lista_produtos else ["Nenhum item em estoque"])
        
        if not df_estoque.empty and produto_selecionado in df_estoque['Produto'].values:
            qtd_atual = df_estoque.loc[df_estoque['Produto'] == produto_selecionado, 'Quantidade'].values[0]
            if 0 < qtd_atual <= 2:
                st.error(f"Estoque crítico! Restam apenas {qtd_atual} unidades.")
            elif qtd_atual == 0:
                st.error("ERRO: Produto esgotado no estoque.")

        with st.form("form_venda", clear_on_submit=True):
            # CAMPOS IDENTICOS À SUA FOTO
            cliente_venda = st.text_input("Identificação do Cliente (Nome/CPF)")
            obs_venda = st.text_area("Observações da Venda")
            cat_prod = st.selectbox("Categoria", ["periféricos", "acessorios", "celulares", "peças de hardware", "eletrodomésticos", "serviços e manutenção"])
            valor_venda = st.number_input("Valor da Transação (R$)", value=None, placeholder="0,00", step=0.01)
            forma_pgto = st.radio("Forma de Pagamento", ["Pix", "Cartão", "Boleto", "Dinheiro"], horizontal=True)
            
            if st.form_submit_button("REGISTRAR TRANSAÇÃO"):
                if lista_produtos and valor_venda is not None and valor_venda > 0:
                    qtd_dis = df_estoque.loc[df_estoque['Produto'] == produto_selecionado, 'Quantidade'].values[0]
                    eh_servico = cat_prod == "serviços e manutenção"
                    
                    if eh_servico or qtd_dis > 0:
                        if not eh_servico:
                            df_estoque.loc[df_estoque['Produto'] == produto_selecionado, 'Quantidade'] = qtd_dis - 1
                            df_estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
                        
                        nova_v = {'Data': datetime.now().strftime("%d/%m/%Y"), 'Hora': datetime.now().strftime("%H:%M:%S"), 'Cliente': cliente_venda, 'Produto': produto_selecionado, 'Categoria': cat_prod, 'Valor (R$)': valor_venda, 'Pagamento': forma_pgto, 'Observações': obs_venda}
                        pd.concat([df_vendas, pd.DataFrame([nova_v])], ignore_index=True).to_csv(ARQUIVO_VENDAS, index=False)
                        st.success("Venda registrada com sucesso.")
                        st.rerun()
                    else:
                        st.error("Não dá pra vender, tá sem estoque.")

    with col_v2:
        # INDICADORES DE FATURAMENTO (A COLUNA DA DIREITA)
        st.subheader("Indicadores de Faturamento")
        if not df_vendas.empty:
            filtro = st.radio("Ver faturamento de:", ["Visualizar Hoje", "Visualizar por Mês"], horizontal=True)
            
            if filtro == "Visualizar Hoje":
                hoje_str = datetime.now().strftime("%d/%m/%Y")
                df_final = df_vendas[df_vendas['Data'] == hoje_str]
                rotulo = "Hoje"
            else:
                df_vendas['Mes_Ano'] = df_vendas['Data'].apply(lambda x: x[3:])
                m_sel = st.selectbox("Escolha o Mês/Ano:", sorted(df_vendas['Mes_Ano'].unique().tolist(), reverse=True))
                df_final = df_vendas[df_vendas['Mes_Ano'] == m_sel]
                rotulo = m_sel

            st.metric(f"Total faturado ({rotulo})", f"R$ {df_final['Valor (R$)'].sum():.2f}")
            fig = px.pie(df_final, values='Valor (R$)', names='Categoria', hole=0.4, title=f"Divisão por categoria ({rotulo})")
            st.plotly_chart(fig, use_container_width=True)
            st.write("Últimos lançamentos:")
            st.dataframe(df_final.tail(10), use_container_width=True)
        else:
            st.info("Aguardando lançamentos para gerar indicadores.")