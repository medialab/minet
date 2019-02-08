# =============================================================================
# Minet HTML Content Extraction Function
# =============================================================================
#
# A function extracting the relevant text content from a HTML file.
#
import os
import csv
import dragnet


def HTML_to_content(string, url_id, folder):
    try:
        extraction_result = dragnet.extract_content(string)
    except Exception as e:
        print('Dragnet extraction error:', e)
        extraction_result = 'Dragnet extraction error'

    with open(os.path.join(folder, 'contentfiles', url_id + '.txt'), 'w') as result:
        result.write(extraction_result)

    return extraction_result


def extract_content(data_path, monitoring_file_path, id_column='id'):
    content_files_path = os.path.join(data_path, 'contentfiles')
    html_files_path = os.path.join(data_path, 'html')
    nb_of_processed_files = 0
    if not os.path.exists(content_files_path):
        os.makedirs(content_files_path)
    with open(monitoring_file_path, 'r') as monitoring_file:
        reader = csv.reader(monitoring_file)
        headers = next(reader, None)
        id_position = headers.index(id_column)
        for line in reader:
            file_id = line[id_position]
            if not os.path.isfile(os.path.join(data_path, 'contentfiles', file_id + '.txt')):
                with open(os.path.join(html_files_path, file_id + '.html'), 'r') as f:
                    html_string = f.read()
                    content = HTML_to_content(
                        html_string, file_id, data_path)
                nb_of_processed_files += 1
                print("Content of " + file_id + " extracted to " + content_files_path +
                      file_id + ".txt (File n°" + str(nb_of_processed_files) + ")")


if __name__ == '__main__':
    extract_content('data', 'data/monitoring.csv')
