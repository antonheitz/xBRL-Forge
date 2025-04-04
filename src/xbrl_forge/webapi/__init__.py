import os
import shutil
import logging
import json
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse

from ..utils.tmp_dirs import create_tmp_dir, remove_tmp_dir
from ..__init__ import convert_document, validate_input_data, load_input_data, create_xbrl, InputData

logger = logging.getLogger(__name__)

def save_file(tmp_dir: str, file: UploadFile) -> str:
    filepath: str = os.path.join(tmp_dir, file.filename)
    logger.info(f"Saving uploaded file to {filepath}")
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return filepath

app = FastAPI()

@app.get("/")
async def root():
    return {"xbrl-forge": "Hello There!"}

@app.post("/convert_document")
async def convert_document_endpoint(document: UploadFile = File(...)):
    try:
        tmp_dir: str = create_tmp_dir()
        document_filepath: str = save_file(tmp_dir, document)
        return convert_document(document_filepath).to_dict()
    finally:
        remove_tmp_dir(tmp_dir)

@app.post("/validate_input_data")
async def validate_input_data_endpoint(input_data: str = Form(...)):
    valdation_result: dict = {
        "valid": True,
        "message": "The input data is valid against the JSON Schema"
    }
    try:
        input_data_dict: dict = json.loads(input_data)
        validate_input_data(input_data_dict)
    except Exception as e:
        valdation_result["valid"] = False
        valdation_result["message"] = str(e)
    return valdation_result

@app.post("/create_xbrl")
async def create_xbrl_endpoint(bg_tasks: BackgroundTasks, input_data_list: str = Form(...), xthml_template: str = Form(None)):
    loaded_data_dicts: List[dict] = json.loads(input_data_list)
    loaded_data: List[InputData] = [load_input_data(input_data_dict) for input_data_dict in loaded_data_dicts]
    result = create_xbrl(loaded_data, xthml_template)
    try:
        tmp_dir: str = create_tmp_dir()
        bg_tasks.add_task(remove_tmp_dir, tmp_dir)
        file_path: str = result.create_package(tmp_dir)
        return FileResponse(file_path, background=bg_tasks, headers={'Content-Disposition': f'attachment; filename={file_path.split("/")[-1]}'})
    except Exception as e:
        logger.error(str(e))
        remove_tmp_dir(tmp_dir)
    