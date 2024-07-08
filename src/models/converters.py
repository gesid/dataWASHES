from csv import writer
from io import StringIO

def flatten_dict(data: dict, parent_key='', sep='.') -> dict:
    flat_dict = []
    for key, value in data.items():
        new_key = f'{parent_key}{sep}{key}' if parent_key else key
        if isinstance(value, dict):
            flat_dict.extend(flatten_dict(value, new_key, sep).items())
        else:
            flat_dict.append((key, value))
    return dict(flat_dict)

def convert_to_csv(data):
    if not data:
        return ""
    print(data)
    output = StringIO()
    csv_writer = writer(output)
    
    if isinstance(data, list):
        flatten_data = [flatten_dict(row) for row in data]
        csv_writer.writerow(flatten_data[0].keys())
        for item in flatten_data:
            csv_writer.writerow(item.values())
    else:
        flatten_data = flatten_dict(data)
        csv_writer.writerow(flatten_data.keys())
        csv_writer.writerow(flatten_data.values())
    

    return output.getvalue()


