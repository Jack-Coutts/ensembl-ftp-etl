# ETL of GFF files from Ensembl Plants

## Introduction

This repo contains a Python script for extracting, transforming, and loading (ETL) gene information from [GTF](https://www.ensembl.org/info/website/upload/gff.html) files downloaded from the [Ensembl plants FTP server](https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/). The script was done as a timed task and completed in approx 2.5 hours.


## Features

* Download GTF files from the Ensembl FTP server for a specified species and release
* Unzip downloaded GTF files
* Parse GTF files and extract relevant gene information
* Transform data into a simplified format
* Output results as TSV files


## Requirements

* [Python](https://www.python.org/downloads/) 3.12 or higher
* [Poetry](https://python-poetry.org/docs/) for dependency management
* [wget](https://www.gnu.org/software/wget/) command-line tool (for downloading files from FTP server)

On MacOS, you can install all of the above using [Homebrew](https://brew.sh/).


## Installation

1. git clone this repository `git clone https://github.com/Jack-Coutts/ensembl-ftp-etl.git`
2. `cd` into the repository directory e.g. `cd ensembl-ftp-etl`
3. Install the dependancies using Poetry `poetry install`. This will create a virtual environment and install all necessary dependencies as specified in the pyproject.toml file.
4. This allows you to run the script using `poetry run python main.py [options]`

Poetry is not necessary for this but is reccomended. If you don't want to use Poetry you can install the dependancies using pip and create a virtual environment with venv (or whatever you prefer).


## Usage Instructions

Assuming the dependancies have been installed you can run the script with the following command: 

```bash
poetry run python main.py --release <release> --species <species>

```

In this command you need to replace `<release>` and `<species>` with the release number and species name respectively.


Where `<species>` is the name of the species you want to download GTF files for and `<release>` is the release number of the Ensembl release version. For example, to download GTF files for *Brassica Juncea* from release 56, you would run:

```bash
poetry run python main.py --release 56 --species brassica_juncea

```

You can browse the available data [here](https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/).


If you have installed the dependancies yourself then the command for running the script would look like the one below:

```bash
python(3) main.py --release <release> --species <species>

```

The you be informed of the location of the downloaded files and the output files, but generally they can be found here:

* Downloaded: `~/temp-ftp-downloads/`
* Output: `~/ensembl-ftp-etl-output/`

## Configuration

The script uses several constants that **can**, but should not need to be, modified in the main.py file:

`default_ensembl_ftp_url`: The base URL for the Ensembl FTP server
`temp_download_folder`: The folder for downloaded files
`output_folder`: Folder for the final output TSV files


## To Do / Next Steps

* Add unit testing
* Add more file-type compatability (e.g. GFF3)
* Add more command line options (e.g. output to CSV or TSV, delete or keep downloaded GTF files)
* Add better/more error handling
* Improve Speed/Efficiency
* Add more documentation
* Create an executable for easy installtion for one time users
* Add CLI as an easier UI (would be optional as worse for pipeline integration)
* Make more verbose (e.g. time operations and feedback to user)
