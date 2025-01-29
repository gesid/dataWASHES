import pandas as pd
import json


def main():
    df = pd.read_excel('dataWASHES-data.xlsx')

    paperJson = []
    authors = {}
    paper_counter = 0
    author_counter = 0

    for i in range(len(df.index)):

        if df.loc[i, "Authors"] in authors:
            author_id = authors[df.loc[i, "Authors"]]
        else:
            author_id = author_counter
            authors[df.loc[i, "Authors"]] = author_id
            author_counter += 1

        author = {
            "Name": df.loc[i, "Authors"],
            "Institution": df.loc[i, "Author's institution"],
            "State": df.loc[i, "Author's state of Brazil"],
            "Author_id": author_id,
            "Institution_acronym": df.loc[i, "Institution's Acronym"]
        }

        if pd.notna(df.loc[i, "Paper's title"]):
            paper = {}
            paper["Paper_id"] = paper_counter
            paper["Title"] = df.loc[i, "Paper's title"]
            paper["Language"] = df.loc[i, "Language"] 
            paper["Year"] = int(df.loc[i, "Year"])
            paper["Abstract"] = df.loc[i, "Abstract"]
            paper["Resumo"] = df.loc[i, "Resumo"]
            paper["Keywords"] = df.loc[i, "Palavras-chave"]
            paper["Type"] = df.loc[i, "Full paper, short paper or poster"]
            paper["Download_link"] = df.loc[i, "Link"]
            paper["References"] = df.loc[i, "Referências"].strip().split(sep='\n\n')
            paper["Cited_by"] = str(df.loc[i, "Citações"]).strip().split(sep='\n')
            paper["Updated_in"] = str(df.loc[i, "Data de obtenção"].date())
            paper["Authors"] = []
            # paper classifications attributes
            paper["Approach"] = df.loc[i, "Quanto à abordagem"]
            paper["Objective"] = df.loc[i, "Quanto aos objetivos"]
            paper["Procedures"] = df.loc[i, "Quanto aos procedimentos"]
            paper["Data_collection"] = df.loc[i, "Método para coleta de dados"]
            paper["Quantitative_Data_Analysis"] = df.loc[i, "Método para análise de dados quantitativos"]
            paper["Qualitative_Data_Analysis"] = df.loc[i, "Método para análise de dados qualitativos"]

            paperJson.append(paper)
            paper_counter += 1

        paper["Authors"].append(author)

    with open('papers.json', 'w', encoding='utf-8') as json_file:
        json.dump(paperJson, json_file, sort_keys=False)


if __name__ == "__main__":
    main()
