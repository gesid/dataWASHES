import pandas as pd
import json


def main():
    df = pd.read_excel('dataWASHES-data.xlsx')

    authorJSON = []
    authors = {}
    paper_counter = -1
    author_counter = 0

    for i in range(len(df.index)):
        if pd.notna(df.loc[i, "Paper's title"]):
            paper_counter += 1

        if df.loc[i, "Authors"] in authors:
            author_id = authors[df.loc[i, "Authors"]]
            authorJSON[author_id]["Papers"].append(paper_counter)
        else:
            author_id = author_counter
            author = {
                "Name": df.loc[i, "Authors"],
                "Institution": df.loc[i, "Author's institution"],
                "State": df.loc[i, "Author's state of Brazil"],
                "Author_id": author_id,
                "Institution_acronym": df.loc[i, "Institution's Acronym"],
                "Papers": [paper_counter]
            }
            authorJSON.append(author)
            authors[df.loc[i, "Authors"]] = author_id
            author_counter += 1

    with open('authors.json', 'w', encoding='utf-8') as json_file:
        json.dump(authorJSON, json_file, sort_keys=False)


if __name__ == "__main__":
    main()
