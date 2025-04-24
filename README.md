# Telecomunication Towers Inspection

## Overview

This project provides a set of tools designed to process and analyze images of telecommunication towers. The primary objective is to assist in the inspection and maintenance of these structures by automating image processing tasks.

## Features

- **Image Processing Pipeline**: Automates the processing of tower images to identify and highlight areas of interest.
- **Metadata Handling**: Utilizes `metadata.json` to store and manage information related to the images.
- **Utility Scripts**: Includes scripts for renaming files and other auxiliary tasks to streamline the workflow.

## Repository Structure

- `main.py`: The main script that orchestrates the image processing workflow.
- `mainOld.py`: A previous version of the main script, retained for reference.
- `rename.py`: A utility script to rename image files according to a specific convention.
- `utils/`: A directory containing helper functions and modules used across the project.
- `metadata.json`: A JSON file storing metadata associated with the images.
- `requirements.txt`: Lists the Python dependencies required to run the project.
- `Guia de Procesamiento.pdf`: A processing guide detailing the steps and methodologies employed.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mgnavarrete/TelecomunicationTowersInspection.git
   cd TelecomunicationTowersInspection
   ```

2. **Create a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare Images**: Place the images of telecommunication towers you wish to process in a designated directory.

2. **Run the Main Script**:
   ```bash
   python main.py
   ```

   This will initiate the processing pipeline, applying the necessary transformations and analyses to the images.

3. **Review Results**: Processed images and any generated reports or data will be available in the output directory specified within the script.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
