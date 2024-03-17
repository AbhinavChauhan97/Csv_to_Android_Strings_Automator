import xml.etree.ElementTree as ET
import csv
import os
from collections import OrderedDict
from bs4 import BeautifulSoup
from array_medium_problems import rearrangeBySign
from array_medium_problems import find_leaders
import keyword
from lxml import etree
import re
import tkinter as tk
import asyncio
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

android_locales = {
    'as': 'Assamese',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'ne': 'Nepali',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'sl': 'Slovak',
    'tr': 'Turkish',
    'hi': 'Hindi',
    'ur': 'Urdu',
    'bn': 'Bengali',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'or': 'Odia',
    'gu': 'Gujarati',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'sd': 'Sindhi',
    'sk': 'Slovak',
    'sn': 'Shona',
    'si': 'Sinhala',
    'bo': 'Tibetan',
    'sl': 'Slovenian',
    'sw': 'Swahili',
    'tl': 'Tagalog',
    'uk': 'Ukrainian',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'ka': 'Georgian',
    'kn': 'Kannada',
    'xh': 'Xhosa',
    'mi': 'Maori',
    'yo': 'Yoruba',
    'zu': 'Zulu',
}

def create_list_box(root):
    frame = Frame(root)
    scrollbar = Scrollbar(frame,orient=VERTICAL)
    list_box = Listbox(frame,yscrollcommand=scrollbar.set)
    scrollbar.config(command=list_box.yview)
    scrollbar.pack(side = RIGHT,fill = Y)
    frame.place(relx = 0.5,rely=0,relwidth=0.5, relheight=1)
    list_box.pack(pady=20, fill=tk.BOTH, expand=True)
    return list_box

def choose_strings_directory():
    directory_path = filedialog.askdirectory()
    lang_name_and_code_dict = get_app_languages(directory_path)

    if lang_name_and_code_dict is None:
        messagebox.showinfo("Alert","Selected directory doesn't seem like res directory of android project")
    else:
       # find_duplicates_button.config(state=tk.NORMAL,command=lambda : find_duplicate_strings_in_all_files(directory_path))f"{directory_path}/values/strings.xml"
        choose_csv_button.config(state=tk.NORMAL, command=lambda : choose_translations_csv(directory_path,os.path.join(directory_path,"values","strings.xml"),lang_name_and_code_dict))

def find_duplicate_strings_in_all_files(directory_path):
    duplicate_strings_messages = []
    async def async_job():
        all_strings_files = [os.path.join(directory_path,f"{dir}","strings.xml") for dir in os.listdir(directory_path) if
                             dir.startswith('values')]
        duplicates = []
        #for path in all_strings_files:
        duplicates.append(find_duplicate_strings(all_strings_files[0]))


        for duplicates_dict in duplicates:
            for string in duplicates_dict:
                duplicate_strings_messages.append(string)
                print(duplicate_strings_messages)
        return duplicate_strings_messages

    async def async_and_main():
        strings = await async_job()
        for message in duplicate_strings_messages:
            list_box.insert(tk.END,message)


    asyncio.run(async_and_main())

def choose_translations_csv(res_directory_path,strings_file_path,lang_name_and_code_dict:dict[str,str]):
    csv_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    get_keys_for_new_strings(res_directory_path,strings_file_path,csv_file_path,lang_name_and_code_dict)

def get_app_languages(res_path: str) -> dict[str, str]:

    res_directories = os.listdir(res_path)
    language_codes = [dir.split('-')[1] if dir.__contains__('-') else 'en' for dir in res_directories if
                      dir.startswith('values')]
    if len(language_codes) == 0:
        return None
    else:
        supported_languages_key_values = {code: android_locales[code] for code in language_codes if code in android_locales}
        return supported_languages_key_values

def read_row(file_path, row_index):
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for i in range(row_index + 1):
            row = next(csv_reader)
            if (i == row_index):
                return row

def contains_html(content):
    # Check if the content contains HTML-like tags
     return  '<' in content and '>' in content

def merge_strings(res_path: str, lang_code: str, dictionary: dict[str, str]):
    xml_file_path = os.path.join(res_path, f"values-{lang_code}", "strings.xml")
    try:
        # Read the existing content of the XML file
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            existing_content = file.read()

        # Find the index where the closing </resources> tag is
        end_resources_index = existing_content.rfind('</resources>')

        if end_resources_index != -1:
            # Add newline before adding new resources
            new_content = existing_content[:end_resources_index] + '\n'
            root = etree.fromstring(existing_content)

            existing_keys = {elem.get('name') for elem in root.findall('.//string')}
            # Add new string resources
            for key, value in dictionary.items():
                if key not in existing_keys:
                    new_string = f'  <string name="{key}">{value}</string>\n'
                    new_content += new_string
                    list_box.insert(tk.END,f" added new string {new_string}")
                else:
                    list_box.insert(tk.END,f" value {value} already exists with key {key}")


            # Add the closing </resources> tag
            new_content += '</resources>\n'

            # Write the updated content back to the file
            with open(xml_file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)

            #list_box.insert(0,f"String resources added successfully.")
        else:
            messagebox.showinfo("Alert","Error: Couldn't find </resources> tag in the XML file.")
    except Exception as e:
        if type(e) == ValueError:
            messagebox.showinfo("Alert", f"""Error adding string resources: {e}\nMake sure <resources> is root tag of {android_locales[lang_code]} string file and not  <?xml version="1.0" encoding="utf-8"?> or anything else""")
        else:
            messagebox.showinfo("Alert",f"Error adding string resources: {e}")

def create_strings_xml(keys, output_folder, column_values):
    try:
        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Create a strings.xml file with column values
        strings_xml_path = os.path.join(output_folder, 'strings.xml')
        with open(strings_xml_path, 'w', encoding='utf-8') as output_file:
            output_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
            output_file.write('<resources>\n')

            for index in range(len(column_values)):
                value = column_values[index]
                if (value.strip()):
                    output_file.write(f'    <string name="{keys[index]}">{column_values[index]}</string>\n')

            output_file.write('</resources>\n')

        messagebox.showinfo("Success",f"Strings.xml file created successfully at {strings_xml_path}")

    except Exception as e:
        messagebox.showinfo("Alert",f"An error occurred: {e}")

def read_column(file_path, column_index):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            # Create a CSV reader
            csv_reader = csv.reader(csvfile)

            # Skip the header row
            next(csv_reader)

            # Read the specified column
            column_values = [row[column_index] for row in csv_reader]
            # skipped_blanks = [string for string in column_values if string.strip()]

            return column_values

    except FileNotFoundError:
        messagebox.showinfo("Alert",f"The file at path {file_path} was not found.")
        return None
    except IndexError:
        messagebox.showinfo("Alert",f"Column index {column_index} is out of range.")
        return None
    except Exception as e:
        messagebox.showinfo("Alert",f"An error occurred: {e}")
        return None

def get_keys_and_index_in_strings_file_using_default_values(keys_file_path, values):
    try:
        # Parse the strings file
        tree = ET.parse(keys_file_path)
        root = tree.getroot()

        # Dictionary to store key-value pairs
        keys = {}

        # Iterate through <string> elements
        for string_element in root.findall('.//string'):
            key = string_element.get('name')
            value = string_element.text

            if (value in values):
                index = values.index(value)
                keys[index] = key
        return keys



    except FileNotFoundError:
        messagebox.showinfo("Alert",f"The file at path {keys_file_path} was not found.")
        return None
    except ET.ParseError as e:
        messagebox.showinfo("Alert",f"Error parsing XML: {e}")
        return None
    except Exception as e:
        messagebox.showinfo("Alert",f"An error occurred: {e}")
        return None

def find_duplicate_strings(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Dictionary to store encountered values and their corresponding keys
        value_dict = {}
        duplicates_string = []
        # Iterate through <string> elements
        for string_element in root.findall('.//string'):
            # Extract the attribute values
            name = string_element.get('name')
            value = string_element.text

            # Check if the value is already in the dictionary
            if value in value_dict:
                # Duplicate value found
                duplicates_string.append(f"Duplicate Found: key is {value_dict[value]} value is {value}")
                # print(f"Duplicate Value: {value}")
                # print(f"  Key 1: {value_dict[value]}")
                # print(f"  Key 2: {name}")
                # print("")

            # Store the value and its corresponding key in the dictionary
            value_dict[value] = name


    except FileNotFoundError:
        print(f"The file at path {file_path} was not found.")
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return duplicates_string


def key_values_for_language(csv_file_path: str,lang_code:str, index: int, keys: list[str]):
    list_box.insert(tk.END, "\n\n")
    list_box.insert(tk.END, f" In {android_locales[lang_code]} language string file")
    list_box.insert(tk.END,"\n")
    strings = read_column(csv_file_path, index)
    key_values = {}
    for i in range(len(strings)):
        word = strings[i]
        if word != '':
            if keys.__contains__(i):
                key_values[keys[i]] = word
            else:
                list_box.insert(tk.END,f" No key found for {word} in default strings file")
    return key_values


def get_keys_for_new_strings(res_directory_path,strings_xml_path:str,csv_file_path: str,code_and_name_dict):
    languages = read_row(csv_file_path, 0)
    lower_case_languages = [lang.lower() for lang in languages]
    english_index = lower_case_languages.index('english')
    english_strings = read_column(csv_file_path, english_index)
    keys = get_keys_and_index_in_strings_file_using_default_values(strings_xml_path, english_strings)

    for key, value in code_and_name_dict.items():
        if lower_case_languages.__contains__(value.lower()):
            if value.lower() != 'english':
                lang_index = lower_case_languages.index(value.lower())
                key_value_pair_for_lang = key_values_for_language(csv_file_path,key, lang_index, keys)
                merge_strings(res_directory_path, key, key_value_pair_for_lang)


# strings_xml_path = "strings.xml"
# csv_file_path = "translations.csv"
# res_path = r'C:\Users\mi\AndroidStudioProjects\android_revamp\app\src\main\res'

# languages = read_row(csv_file_path, 0)

root = tk.Tk()
root.title("Choose the android project res directory")
choose_project_button = tk.Button(root, text="Choose res directory", command=choose_strings_directory)
choose_project_button.place(relx=0.1,rely=0.1)
choose_project_button_info_label = Label(root,text="Go the res for of your android project and click ok",font=("Helvetica", 8) )
choose_project_button_info_label.place(relx = 0.15,rely=0.18)
choose_csv_button = tk.Button(root, text="     Choose CSV File    ", state=tk.DISABLED)  # Initially disabled
choose_csv_button_info_lablel = Label(root,text="Choose your translations csv file\nthe first row of the file should be languages names row\nplease make sure all the names are correctly spelled\nand the second row is blank\nthen comes your translations",font=("Helvetica", 8))
choose_csv_button.place(relx=0.1,rely=0.3)
choose_csv_button_info_lablel.place(relx = 0.15,rely=0.38)

# find_duplicates_button = tk.Button(root, text="Find duplicate strings", state=tk.DISABLED)
# find_duplicates_button.place(relx=0.1,rely=0.6)
# find_duplicates_button_info_label = Label(root,text="Find the duplicate strings with differnet keys in your strings.xml file",font=("Helvetica", 8) )
# find_duplicates_button_info_label.place(relx = 0.15,rely=0.65)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# Calculate the desired width and height
width = int(0.7 * screen_width)
height = int(0.7 * screen_height)

list_box = create_list_box(root)





# Set the width and height of the window
root.geometry(f"{width}x{height}")
root.mainloop()