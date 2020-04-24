#imports
import streamlit as st
import pandas as pd
import numpy as np

#importing dataframes
view_aluno = pd.read_csv('view_aluno.csv')
view_materias = pd.read_csv('view_materias.csv').drop('Unnamed: 0',axis=1)
respostas = pd.read_csv('respostas.csv')
curso_pretendido = pd.read_csv('curso_pretendido.csv')
respostas = pd.read_csv('respostas.csv')
view_qtd_curso = pd.read_csv('view_qtd_curso.csv')
view_curso = pd.read_csv('view_curso.csv')

#Transformação view_curso para percentual por curso
view_curso_sum = view_curso.groupby('Cursos').sum().drop(['Percentual'],axis=1).reset_index().rename({'Correção':'Total_Acerto'},axis=1)
view_curso_count = view_curso.groupby('Cursos').count().drop(['Correção','Percentual'],axis=1).reset_index().rename({'CPF':'Total_Questoes'},axis=1)
view_curso_count['Total_Questoes'] = view_curso_count['Total_Questoes']*60
view_curso_perc = view_curso_count.merge(view_curso_sum,how='left',left_on='Cursos',right_on='Cursos')
view_curso_perc['Percentual_Acerto'] = view_curso_perc['Total_Acerto']/view_curso_perc['Total_Questoes']
view_curso_perc.drop(['Total_Questoes','Total_Acerto'],axis=1,inplace=True)


#Page styling
h1 = '''

<div style="text-align:center;background-color:PaleTurquoise;padding:15px;border-radius:5px;width:775px"> 
	<p style="font-size:50px"> Painel Einstein </p>
</div>

'''

h2 = '''

<div style="text-align:center"> 
	<p style="font-size:25px"> Bem vindo ao Painel Einstein, um portal para vizualização do desempenho dos Einsteinianos nos simulados </p>
</div>

'''

st.markdown(h1,unsafe_allow_html=True)

st.markdown(h2,unsafe_allow_html=True)

lista_relatorios = ['Relatório geral','Relatório Aluno','Relatório Curso','Sobre o Einstein Floripa']
sidebar_opt = st.sidebar.selectbox('Escolha o tipo de Relatório',lista_relatorios)


#Reports options
#Relatorio Geral
if sidebar_opt == 'Relatório geral':

	st.title('Relatório geral das matérias:')

	tabela_pont_geral = view_materias.drop(['Total_Questoes'],axis=1)

	formatacao = {'Percentual_Acerto_Geral':"{:.2%}",'STD':"{:.2%}"}
	st.table(tabela_pont_geral.style.format(formatacao))

	st.title('Relatório geral dos cursos:')
	st.table(view_curso_perc.style.format({'Percentual_Acerto':"{:.2%}"}))
#Relatorio aluno
elif sidebar_opt == 'Relatório Aluno':

	st.title('Relatório Aluno:')

	tabela_cpfs = curso_pretendido['CPF']
	cpf = st.selectbox('CPF para consulta:',tabela_cpfs).strip()

	tabela_pont_alunos = view_aluno[view_aluno['CPF']==cpf].drop('CPF',axis=1)

	curso_aluno = list(curso_pretendido[curso_pretendido['CPF']==cpf]['Cursos'].values)[0]

	total_acertos = tabela_pont_alunos['Pontuação_aluno'].sum()
	percentual_acerto = total_acertos/60

	concorrentes_curso = view_qtd_curso[view_qtd_curso['Cursos']==curso_aluno]['CPF'].values[0]

	texto_header_aluno = f'Curso pretendido: {curso_aluno} | Total de acertos: {total_acertos} | Percentual de acerto: {percentual_acerto:.2%} | Concorrentes no curso: {concorrentes_curso}'

	st.subheader(texto_header_aluno)

	st.table(tabela_pont_alunos.style.format({'Percentual_Acerto':"{:.2%}"}))

#Relatorio Curso
elif sidebar_opt == 'Relatório Curso':

	st.title('Relatório Curso:')

	list_cursos = view_curso['Cursos'].sort_values().unique()
	curso_select = st.selectbox('Curso para consulta:',list_cursos)
	
	view_curso_filtrado = view_curso[view_curso['Cursos']==curso_select]['Correção']
	len_view_curso_filtrado = len(view_curso_filtrado)*60
	perc_acerto_curso = (view_curso_filtrado.sum())/(len_view_curso_filtrado)

	concorrentes_curso = view_qtd_curso[view_qtd_curso['Cursos']==curso_select]['CPF'].values[0]
	texto_header_curso = f'Concorrentes no curso: {concorrentes_curso} | Acerto do Curso: {perc_acerto_curso:.2%}'

	st.subheader(texto_header_curso)


	tabela_curso = view_curso[view_curso['Cursos']==curso_select]
	st.table(tabela_curso.drop(['Correção','Cursos'],axis=1).style.format({'Percentual':"{:.2%}"}))

#Sobre
elif sidebar_opt == 'Sobre o Einstein Floripa':

	st.subheader('Um pouco sobre o Einstein Floripa:')

	st.video('https://www.youtube.com/watch?v=aj8RBrr4vqs')

	st.markdown('## Para saber mais acesse nosso [site](https://einsteinfloripa.com.br/)')
