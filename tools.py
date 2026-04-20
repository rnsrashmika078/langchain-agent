from datetime import datetime
import json
from zoneinfo import ZoneInfo
import requests
from langchain_core.tools import tool
import os
from typing import List, Any, Literal, Dict


@tool
def normal_chat(prompt: str) -> str:
    """casual chat for user prompt"""
    return f"{prompt}"
@tool
def get_current_time(
    zone: str,
) -> str:
    """return the current time. argument zone example : Asia/Colombo. based on location.only call this when user specifically asked about current time."""
    now = datetime.now(ZoneInfo("Asia/Colombo"))
    return f"current time {now}"
@tool
def dummy_data() -> str:
    """return the dummy data by calling api.only call this when user specifically ask"""
    url = "https://dummyjson.com/test"
    # params = {"latitude": 6.9271, "longitude": 79.8612, "current_weather": True}
    res = requests.get(url)
    # res = requests.get(url, params=params)
    print("dummy data", res.json())
    return res.json()
@tool
def generate_chart(
    data: List[Dict[str, Any]],
    type: Literal["pie", "line"],
    xKey: str,
    yKey: str,
) -> str:
    """
    Generate a chart based on user asked topic.


    Arguments:
        -data: List of objects (chart data ) ( *** LOWERCASE *** )
        -type: Chart type ("pie" or "line") ( *** LOWERCASE *** )
        -xKey: Name for X axis ( example : data is related to sport then xKey is sport ) -> make sure to add relevant name according to the data ( *** LOWERCASE *** )
        -yKey: Name for Y axis ( example : value ) -> make sure to add relevant name according to the data ( *** LOWERCASE *** )
    """
    return f"Chart generated with type={type}, xKey={xKey}, yKey={yKey}"
@tool
def create_update_file(directory: str, fileName: str, content: str) -> str:
    """Create or update a file or folder ( directory ) on the computer.

    if fileName not found .. simple reply file name is required

    For example, if the user says 'create a file called india.txt and add Indian cricket team squad',
    the tool will generate the actual Indian cricket team squad and save it in the file.

    USE PROPER STRUCTURE WHEN INSERT CONTENT TO A FILE SUCH AS INTENT, LINE SPACES , NUMBERS

    *** NOTE ***
    ****** FILE NAME MUST BE CHANGE IF USER EXPLICITLY TELL, OTHERWISE USE THE SAME FILENAME AND PATH
    Arguments:
    - directory: {folderName if any}/{fileName}.{extension} ex:test/file.txt -> don't precede it with like C: and dont precede with '/' at the beginning. use same filename if update the file content
    - fileName : name of the file with extension . ex: file.txt
    - content: The text content to add to the file, generated dynamically by LLM as list with proper indentation and spacing.

    """
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    full_path = os.path.join(desktop, directory)
    folder = os.path.dirname(full_path)
    os.makedirs(folder, exist_ok=True)
    path = full_path

    # print("home", home)
    # print("Full path", full_path)
    # print("directory", directory)
    # # print("folder", folder)
    # print("content", content)
    try:
        if not fileName:
            return {
                "message": "failed to create a folder. fileName not found!‌",
                "file_path": "error while getting file path",
                "content": "no content",
                "operation": "null",
            }
        if not directory:
            path = os.path.join(full_path, fileName)
        with open(path, "w") as f:
            f.write(content)
            if os.path.isfile(full_path):
                return f"file updated at ${full_path} with the content of ${content}"
            else:
                return f"file created at ${full_path} with the content of ${content}"

    except Exception as e:
        return {
            "message": str(e),
            "file_path": "error while getting file path",
            "content": "no content",
            "operation": "null",
        }
@tool
def read_file(directory: str, fileName: str) -> str:
    """read a file or folder ( directory ) on the Desktop.

    --if fileName not found .. simple reply file name is required

    Arguments:
    - directory: {folderName if any}/{fileName}.{extension} ex:test/file.txt -> don't precede it with like C:
    - fileName : name of the file with extension . ex: file.txt
    """
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    full_path = os.path.join(desktop, directory)
    path = full_path

    print("home", home)
    print("Full path", full_path)
    print("directory", directory)
    print("desktop", desktop)
    print("fileName", fileName)

    try:
        if not directory:
            path = os.path.join(desktop, fileName)
        with open(path, "r") as f:
            data = f.read()
            print("data", data)

        return f"data read successfully from the file: data:{data}"
    except Exception as e:
        return f"Failed to create file: {e}"
@tool
def generate_files_with_python_code(python_code: str, file_name: str, save_path: str):
    """generate python code for generate file based on user given input.
        - Use ONLY FILE_PATH to save files
        - Do NOT use file_name or hardcoded paths
        - Assume FILE_PATH is given
        - Output clean Python code only
    Arguments:
        save_path:python code save path must change to this Path: default path : = C:\\Users\\Rashm\\OneDrive\\Desktop\\NEXT JS\\Next\\public/files/
        python_code: python code snippet for generate file
        file_name:name for file. example: hello.txt
    """

    modified = f"public/files/{file_name}"
    project_dir = r"C:\Users\Rashm\OneDrive\Desktop\NEXT JS\Next"
    newPath = os.path.join(project_dir, modified)
    python_code = f"FILE_PATH = r'{newPath}'\n" + python_code

    for i in range(0, 3):
        try:
            print(f"code: {python_code}")
            exec(python_code, {}, {})
            return f"successfully created file at {newPath}"
        except Exception as e:
            error = str(e)
            new_code = fix_code(python_code, error)
            python_code = new_code
    return f"error while create a file .. try again later: {python_code}"

@tool
def generate_html_code(html_code: str,file_name: str):
    """
    Generate structured HTML for government PDF forms
    """
    return {
        "type": "html_form",
        "html_code": html_code,
        "file_name" : file_name
    }
def fix_code(code, error):
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="gemma4:e4b", temperature=0)
    prompt = f"""
    You are a Python code fixer. Return ONLY executable Python code. No explanations. No markdown.
    FOR EXCEL ONLY:
        import pandas as pd
        df = pd.DataFrame(...)
        df.to_excel("output.xlsx", index=False)

    ERROR TO FIX:
    {error}

    BROKEN CODE:
    {code}

    FIXED CODE (return only raw Python, no markdown, no explanation):"""

    response = llm.invoke(prompt)
    fixed_code = response.content
    if fixed_code.startswith("```"):
        fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()
    print(f"error: {error}")
    return fixed_code


def save_file(name: str, content: str):
    modified = f"public/files/{name}"
    project_dir = r"C:\Users\Rashm\OneDrive\Desktop\NEXT JS\Next"
    newPath = os.path.join(project_dir, modified)
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    with open(newPath, "w") as f:
        f.write(content)


def pdf_generate(html_code:str,file_name:str):
    try:
        import pdfkit
        
        print("html Code {html_code}" )
        print("file_name {file_name}" )

        path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

        config = pdfkit.configuration(wkhtmltopdf=path)
        pdfkit.from_string(html_code, f"{file_name}.pdf", configuration=config)
    except Exception as e:
        print(str(e))



