import os
import csv
import ast
import xml.etree.ElementTree as ET


def create_raw_xml(template, new_id, new_name, unit, output_dir):
    tree = ET.parse(template)
    root = tree.getroot()

    root.set('id', str(new_id))
    root.set('name', new_name)

    numeric_allowed_values = root.find('.//numeric-allowed-values')
    numeric_allowed_values.set('max-value', '1600000')
    numeric_allowed_values.set('units', unit)

    output_file = os.path.join(output_dir, f"{new_name}.xml")

    tree.write(output_file, encoding="UTF-8", xml_declaration=True)


def create_state_xml(template, state_name, state_id, raw_id, values, output_dir):
    tree = ET.parse(template)
    root = tree.getroot()

    root.set('id', str(state_id))
    root.set('name', state_name)

    derived_from_id = root.find('.//derived-from-id')
    derived_from_id.text = str(raw_id)

    value_ids = root.findall('.//concept-id-allowed-values')
    for value_id in value_ids:
        value_id.set('id', str(raw_id))

    double_elements = root.findall('.//double')
    for idx, element in enumerate(double_elements):
        element.text = str(values[idx])

    output_file = os.path.join(output_dir, f"{state_name}.xml")

    tree.write(output_file, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    processed_data_top_meds_path = os.path.join('..', 'clustering', 'cluster_results.csv')
    
    template_raw_path = 'templates/raw_concept.xml'
    template_state_paths = ['templates/State1bins.xml', 'templates/State2bins.xml', 'templates/State3bins.xml', 'templates/State4bins.xml', 'templates/State5bins.xml']

    output_raw_directory = 'output_xml_files'
    output_state_directory = 'output_state_xml_files'

    if not os.path.exists(output_raw_directory):
        os.makedirs(output_raw_directory)

    if not os.path.exists(output_state_directory):
        os.makedirs(output_state_directory)

    id_raw = 1
    id_state = 1000

    with open(processed_data_top_meds_path, mode='r', newline='') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            med = row['CODE_ATC']
            given_way = row['GIVEN_WAY']
            unit = row['UNIT']
            new_name = f"{med}_{given_way}"
            create_raw_xml(template_raw_path, id_raw, new_name, unit, output_raw_directory)
            k = int(row['K'])

            dict_values = row['RANGES']
            dict_values = ast.literal_eval(dict_values)
            values = []
            for key, val in dict_values.items():
                for v in val.values():
                    values.append(v)
            if k > 1:
                values = values[::-1][1:-1]
            else:
                values = [values[0]]

            state_name = f'{new_name}_state'
            create_state_xml(template_state_paths[k - 1], state_name,  id_state, id_raw, values, output_state_directory)
            id_raw += 1
            id_state += 1

