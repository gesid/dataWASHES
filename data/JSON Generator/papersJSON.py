import pandas as pd
import json

df = pd.read_excel('dataWASHES-data v2 teste.xlsx')

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
        "Institution_acronym": df.loc[i, "Institution's Acronym"],
        "State": df.loc[i, "Author's state of Brazil"],
        "Author_id": author_id,
    }

    if pd.notna(df.loc[i, "Paper's title"]):
        paper = {
            "Paper_id": paper_counter,
            "Title": df.loc[i, "Paper's title"],
            "Year": int(df.loc[i, "Year"]),
            "Abstract": df.loc[i, "Abstract"],
            "Resumo": df.loc[i, "Resumo"],
            "Keywords": df.loc[i, "Palavras-chave"],
            "Type": df.loc[i, "Full paper, short paper or poster"],
            "Download_link": df.loc[i, "Link"],
            "References": df.loc[i, "Referências"].strip().split(sep='\n\n'),
            "Cited_by": df.loc[i, "Citações"].strip().split(sep='\n'),
            "Updated_in": str(df.loc[i, "Data de obtenção"].date()),
            "Language": df.loc[i, "Language"],
            "Authors": [],
        }

        paperJson.append(paper)
        paper_counter += 1

    paper["Authors"].append(author)

with open('../papers.json', 'w', encoding='utf-8') as json_file:
    json.dump(paperJson, json_file, sort_keys=False)
