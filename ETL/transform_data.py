#Import libs
import pandas as pd
import numpy as np

#Importing datasets
def load_data():

	respostas = pd.read_csv('answers.csv')
	database = pd.read_csv('data_base.csv')

	return respostas, database

#Function for mapping subjects
def map_questoes(x):
    if x<=12:
        return 1
    elif x>12 and x<=21:
        return 2
    elif x>21 and x<=28:
        return 3
    elif x>28 and x<=35:
        return 4
    elif x>35 and x<=41:
        return 5
    elif x>41 and x<=48:
        return 6
    elif x>48 and x<=53:
        return 7
    else:
        return 8

#Reading csv files
def transforming_data(respostas,database):

	#Extract from csv and split its columns

	colunas = database.columns[0].split(';')
	colunas[3] = 'Range questoes'
	database.columns = ['values']
	
	#Defines a copy of df for transformations
	df1 = database['values'].str.split(';',expand=True)
	df1.columns = colunas
	df1.fillna(axis=1,value=0,inplace=True)

	#Mapping matérias and creating dataset gabarito and materias
	materias = df1.iloc[:8,[2,3]]
	materias['cod'] = range(1,9)
	gabarito = df1.iloc[:,:2]
	gabarito = gabarito.iloc[:60]
	gabarito['Questão'] = gabarito['Questão'].astype('int')
	gabarito['cod'] = gabarito['Questão'].transform(map_questoes)
	gabarito = gabarito.merge(materias[['cod','Matérias']],how='left',on='cod').drop('cod',axis=1)

	#Separating courses from df1 and creating dataset courses
	cursos = df1.iloc[:,[4,5]]
	cursos = cursos[cursos['Cursos']!='']

	#Creating dataset for applyed course
	curso_pretendido = df1.iloc[:,[6,7]]
	curso_pretendido = curso_pretendido.merge(cursos,how='left',left_on='Curso Pretendido',right_on='Código do Curso')
	curso_pretendido.drop(axis=1,labels=['Curso Pretendido','Código do Curso'],inplace=True)

	#Creating dataset number of person/course
	view_qtd_curso = curso_pretendido.groupby('Cursos').count().reset_index()

	#Mapping the number of questions per subject
	qtd_questoes = dict(gabarito.groupby('Matérias').count().iloc[:,1])

	#Creating intermediate dataset
	materias_map = materias['Matérias'].sort_values().values
	materias_qtd_map = list(gabarito.sort_values('Matérias').groupby('Matérias').count().drop('Questão',axis=1)['Gabarito'].values)
	map_percentual = pd.DataFrame({'Matérias':materias_map,'QTD':materias_qtd_map})
	total_alunos = len(df1.groupby('CPF').sum())
	map_percentual['QTD_Total'] = map_percentual['QTD']*total_alunos

	#Creating the answers dataset
	respostas.columns = ['values']
	respostas = respostas['values'].str.split(';',expand=True)
	respostas = respostas.iloc[1:].melt(0).sort_values([0,'variable'])
	respostas.columns = ['CPF','Questão','Resposta']
	respostas = respostas.merge(gabarito,how='left',left_on='Questão',right_on='Questão')
	respostas = respostas.merge(map_percentual,how='left',left_on='Matérias',right_on='Matérias')
	respostas['Correção'] = np.where(respostas['Resposta']==respostas['Gabarito'],1,0)
	respostas['Percentual'] = np.where(respostas['Resposta']==respostas['Gabarito'],1,0)/respostas['QTD']
	respostas.drop('QTD_Total',axis=1,inplace=True)



	#creating course view
	view_curso = respostas.groupby('CPF').sum().drop(['QTD','Percentual','Questão'],axis=1)
	view_curso['Percentual'] = view_curso['Correção']/60 
	view_curso = view_curso.merge(curso_pretendido,how='left',left_on='CPF',right_on='CPF')
	view_curso.groupby('Cursos').sum().drop(['Percentual'],axis=1).reset_index()

	#Creating intermediate dataset
	materias_map = materias['Matérias'].sort_values().values
	materias_qtd_map = list(gabarito.sort_values('Matérias').groupby('Matérias').count().drop('Questão',axis=1)['Gabarito'].values)
	map_percentual = pd.DataFrame({'Matérias':materias_map,'QTD':materias_qtd_map})
	total_alunos = len(df1.groupby('CPF').sum())
	map_percentual['QTD_Total'] = map_percentual['QTD']*total_alunos

	#Creating subejcts view
	perc_total = map_percentual.drop('QTD',axis=1)
	view_materias = respostas.groupby(['Matérias']).sum().merge(perc_total,how='left',left_on='Matérias',right_on='Matérias')
	view_materias_std = respostas.groupby(['Matérias']).std().merge(perc_total,how='left',left_on='Matérias',right_on='Matérias')
	view_materias_std.drop(['Questão','QTD','Percentual','QTD_Total'],axis=1,inplace=True)
	view_materias['Percentual total'] = view_materias['Correção']/view_materias['QTD_Total']
	view_materias.drop(['Questão','QTD','Percentual'],axis=1,inplace=True)
	view_materias.columns = ['Matéria','Total_Acertos','Total_Questoes','Percentual_Acerto_Geral']
	view_materias = view_materias.merge(view_materias_std,how='left',left_on='Matéria',right_on='Matérias').drop('Matérias',axis=1)
	view_materias.rename({'Correção':'STD'},axis=1,inplace=True)

	#creating students view
	view_aluno = respostas.groupby(['CPF','Matérias']).sum().drop(['Questão','QTD'],axis=1)
	view_aluno.reset_index(inplace=True)
	view_aluno.columns = ['CPF','Matéria','Pontuação_aluno','Percentual_Acerto']
	view_materias_comparacao = view_materias.drop(['Total_Acertos','Total_Questoes'],axis=1)
	view_aluno = view_aluno.merge(view_materias_comparacao,how='left',right_on='Matéria',left_on='Matéria')
	cond_comp_media = view_aluno['Percentual_Acerto'] > view_aluno['Percentual_Acerto_Geral']
	view_aluno['Comparação Média'] = np.where(cond_comp_media,'Acima da Média','Abaixo da Média')
	view_aluno.set_index(['CPF','Matéria'],inplace=True)
	view_aluno.drop(['STD','Percentual_Acerto_Geral'],axis=1,inplace=True)

	return view_aluno, view_materias, respostas, curso_pretendido, view_qtd_curso, view_curso


def save_data(view_aluno,view_materias,respostas,curso_pretendido,view_qtd_curso,view_curso):


	view_aluno.to_csv('view_aluno.csv', header=True, index=True)

	view_materias.to_csv('view_materias.csv', header=True, index=True)

	respostas.to_csv('view_respostas.csv', header=True, index=True)

	curso_pretendido.to_csv('view_curso_pretendido.csv', header=True, index=True)

	respostas.to_csv('view_respostas.csv', header=True, index=True)

	view_qtd_curso.to_csv('view_qtd_curso.csv',header=True,index=False)

	view_curso.to_csv('view_curso.csv',header=True,index=False)

	return None

#Execute function
def main():

	respostas, database = load_data()
	print('Extracting from csv files...')

	view_aluno, view_materias, respostas, curso_pretendido, view_qtd_curso, view_curso = transforming_data(respostas, database)
	print('Transforming data...')


	save_data(view_aluno, view_materias, respostas, curso_pretendido, view_qtd_curso, view_curso)
	print('Saving data into new csv files...')

if __name__ == '__main__':
	main()