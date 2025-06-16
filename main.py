import base64

import streamlit as st
import pandas as pd
import io
import base64


st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)


with open("wallpaper1.png", "rb") as f:
    img = base64.b64encode(f.read()).decode()

# Aplica estilo glass no fundo e nos botões
# Estilo Glass + fundo
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stFileUploaderDropzone"] > div {{
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 1em;
        color: white;
        font-weight: bold;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }}

    [data-testid="stFileUploaderDropzone"] > div:hover {{
        background: rgba(255, 255, 255, 0.25);
        transform: scale(1.02);
    }}
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: white;
        padding: 0.5em 1.5em;
        font-weight: bold;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    button:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.03);
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)


st.title("Gestão de Embarcação")
st.subheader("Controle Operacional e Organizacional para a Ocean Pact")
st.title("")



input_acompanhamento = st.file_uploader("Upload de Acompanhamento", type=["xlsx"])
input_matriz = st.file_uploader("Upload de Matriz", type=["xlsx"])
input_usuario = st.file_uploader("Upload de Usuário", type=["xlsx"])

if input_acompanhamento and input_matriz and input_usuario:
    # Ler os arquivos enviados
    df_acompanhamento = pd.read_excel(input_acompanhamento)
    df_matriz = pd.read_excel(input_matriz)
    df_usuarios = pd.read_excel(input_usuario)




    # Renomear colunas
    df_usuarios = df_usuarios.rename(columns={
        "Nome Alterado": "Nome",
        "Cargo Alterado": "Cargo",
        "Centro de Custo Alterado": "Centro_de_Custo"
    })

    df_matriz = df_matriz.rename(columns={
        "Curso Alterado": "Curso",
        "Cargo Alterado": "Cargo",
        "Centro de Custo Alterado": "Centro_de_Custo",
        "Aplicável?": "Aplicável"
    })

    df_acompanhamento = df_acompanhamento.rename(columns={
        "Nome Alterado": "Nome",
        "Curso Alterado": "Curso",
        "Status": "Status"
    })

    # Filtrar cursos obrigatórios
    matriz_obrig = df_matriz[df_matriz["Aplicável"] == "Obrigatório"].copy()

    # Cursos concluídos
    concluidos = df_acompanhamento[df_acompanhamento["Status"] == "Concluído"].copy()
    concluidos["Concluiu"] = True

    # Processamento
    resultado = []

    for _, pessoa in df_usuarios.iterrows():
        nome = pessoa["Nome"]
        cargo = pessoa["Cargo"]

        centros_relacionados = matriz_obrig[matriz_obrig["Cargo"] == cargo]["Centro_de_Custo"].dropna().unique()
        cursos_feitos = concluidos[concluidos["Nome"] == nome]["Curso"].unique()

        for centro in centros_relacionados:
            cursos_necessarios = matriz_obrig[
                (matriz_obrig["Cargo"] == cargo) &
                (matriz_obrig["Centro_de_Custo"] == centro)
            ]["Curso"].dropna().unique()

            cursos_faltando = [curso for curso in cursos_necessarios if curso not in cursos_feitos]

            if not cursos_faltando:
                status = "Apto"
                faltando = ""
            else:
                status = "Inapto"
                faltando = ", ".join(cursos_faltando)

            resultado.append({
                "Nome": nome,
                "Cargo": cargo,
                "Centro de Custo": centro,
                "Status": status,
                "Faltando": faltando
            })

    df_resultado = pd.DataFrame(resultado)

    st.title("")
    st.subheader("Resultado Final")
    st.dataframe(df_resultado)

    output = io.BytesIO()
    df_resultado.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    st.title("")
    # download

    st.download_button(
        label="Baixar Resultado em Excel",
        data=output,
        file_name="resultado_embarque.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
