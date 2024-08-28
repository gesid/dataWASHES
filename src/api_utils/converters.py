from csv import writer
from io import StringIO


def flatten_dict(data: dict, parent_key='', sep='_') -> dict:
    flat_dict = {}
    for key, value in data.items():
        new_key = f'{parent_key}{sep}{key}' if parent_key else key  # Cria a nova chave composta
        if isinstance(value, dict):
            flat_dict.update(flatten_dict(value, new_key, sep))  # Se o valor for um dicionário, chama recursivamente
        else:
            flat_dict[new_key] = value
    return flat_dict


def remove_dict_list(data: dict, sep='_') -> dict:
    plain_dict = {}
    for key, value in data.items():
        # Processa o caso do valor não ser uma lista
        if not isinstance(value, list):
            plain_dict[key] = value
            continue

        # Processa o caso do valor ser uma lista
        for item in value:
            # Caso não seja uma lista de dicionário encerra o loop
            if not isinstance(item, dict):
                plain_dict[key] = value
                break

            # Caso em que ocorre uma lista de dicionários
            for item_key, item_value in item.items():
                new_key = f'{key}{sep}{item_key}'
                if new_key in plain_dict:
                    plain_dict[new_key].append(item_value)
                else:
                    plain_dict[new_key] = [item_value]
    return plain_dict


def convert_to_csv(data):
    """
    Converts a dictionary to CSV.
    """
    if not data:
        return ""

    output = StringIO()
    csv_writer = writer(output)

    if isinstance(data, list):
        flatten_data = [remove_dict_list(flatten_dict(row)) for row in data]  # Processa cada item da lista

        if flatten_data:
            header_keys = flatten_data[0].keys()
            csv_writer.writerow(header_keys)
            for item in flatten_data:
                csv_writer.writerow(item.values())
    else:
        flatten_data = remove_dict_list(flatten_dict(data))  # Processa o único dicionário

        if flatten_data:
            csv_writer.writerow(flatten_data.keys())
            csv_writer.writerow(flatten_data.values())

    return output.getvalue()
