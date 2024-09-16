import os
import argparse
import gzip
import shutil
import pandas as pd
from subprocess import run

"""Constants"""


default_ensembl_ftp_url = (
    "ftp://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/release-"
)
temp_download_folder = os.path.abspath(
    os.path.expanduser("~/temp-ftp-downloads/")
)
output_folder = os.path.abspath(os.path.expanduser("~/ensembl-ftp-etl-output/"))

"""Functions"""


def download_gtf_files(release: str | int, species: str):
    """
    Download GTF files from Ensembl FTP server

    Args:
        release: Ensembl release version
        species: Ensembl species name
    Returns:
        None
        * Downloads GTF files to temp_download_folder

    """

    wget_command = [
        "wget",
        "-r",  # recursive
        "-l",
        "1",  # limit recursion depth to 1
        "-np",  # don't ascend to the parent directory
        "-nd",  # don't recreate directory structure
        "--directory-prefix",
        temp_download_folder,
        "-A",
        "*.gtf.gz",  # accept only .gtf.gz files
        "-R",
        "*.chr*,*abinitio*",  # reject files containing matching patterns
        f"{default_ensembl_ftp_url}{release}/gtf/{species}/",
    ]
    result = run(wget_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Successfully downloaded to {temp_download_folder}")
    else:
        print(f"Error occurred: {result.stderr}")


def unzip_gtf_files(dir: str | os.PathLike = temp_download_folder):
    """
    Unzip all .gtf.gz files in the temp_download_folder.
    Also deletes the original zipped files.

    Args:
        path: Directory containing .gtf.gz files
    Returns:
        None
        * Unzips .gtf.gz files in the directory
        * Deletes the original .gz files

    """
    for filename in os.listdir(dir):
        if filename.endswith(".gtf.gz"):
            gz_path = os.path.join(temp_download_folder, filename)
            gtf_path = os.path.join(temp_download_folder, filename[:-3])
            with gzip.open(gz_path, "rb") as f_in:
                with open(gtf_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            os.remove(gz_path)  # Delete the original .gz file
            print(f"Unzipped and removed: {filename}")


def read_gtf_file(file: str | os.PathLike) -> pd.DataFrame:
    """
    Read a GTF file into a pandas dataframe

    Args:
        file: Path to the GTF filename
    Returns:
        dataframe: Pandas dataframe containing the GTF data
    """

    dataframe = pd.read_csv(
        file, sep="\t", comment="#", header=None, dtype={0: str}
    )
    dataframe.columns = [
        "seqname",
        "source",
        "feature",
        "start",
        "end",
        "score",
        "strand",
        "frame",
        "attribute",
    ]

    return dataframe


def extract_key_attributes(gtf_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract key attributes from the GTF data and add them as columns

    Args:
        gtf_data: Pandas dataframe containing the GTF dataframe
    Returns:
        gene_data: Pandas dataframe containing the additional columns
    """

    # Select only the rows with "gene" feature
    gene_data = gtf_data[
        gtf_data["feature"] == "gene"
    ].copy()  # Create an explicit copy

    # Regex for extracting attributes
    gene_data.loc[:, "gene_id"] = gene_data["attribute"].str.extract(
        r'gene_id\s*"(.+?)"'
    )
    gene_data.loc[:, "gene_biotype"] = gene_data["attribute"].str.extract(
        r'gene_biotype\s*"(.+?)"'
    )
    return gene_data


def transform_data(gene_data: pd.DataFrame) -> pd.DataFrame:
    """
    Created a new dataframe with only the required columns

    Args:
        gene_data: Pandas dataframe containing the gene dataframe
    Returns:
        output_df: Pandas dataframe containing the required columns
    """

    output_df = gene_data.loc[
        :, ["gene_id", "feature", "gene_biotype", "seqname", "source"]
    ]
    return output_df


def transformation_recursion(
    dir: str | os.PathLike, ouput_file_path: str | os.PathLike = output_folder
):
    """
    Recursively transform all GTF files in the directory-prefix

    Args:
        dir: Directory containing GTF files
        output_folder: Directory to save the transformed unzip_gtf_files
    Returns:
        None
        * Transforms and saves the GTF files in the output_folder
    """

    for filename in os.listdir(dir):
        if filename.endswith(".gtf"):
            file_path = os.path.join(dir, filename)
            raw_data = read_gtf_file(file_path)
            extracted_data = extract_key_attributes(raw_data)
            transformed_data = transform_data(extracted_data)
            out_file_path = os.path.join(
                output_folder, filename[:-4] + ".gene_info.tsv"
            )
            os.makedirs(output_folder, exist_ok=True)
            transformed_data.to_csv(
                out_file_path, sep="\t", header=True, index=False
            )
            print(f"Transformed and saved: {out_file_path}")


"""Main"""


def main():
    parser = argparse.ArgumentParser(description="tbd")
    parser.add_argument("--species", type=str, help="Ensembl species name")
    parser.add_argument("--release", type=int, help="Ensembl release version")
    args = parser.parse_args()

    try:

        download_gtf_files(args.release, args.species)
        unzip_gtf_files()
        transformation_recursion(temp_download_folder)
        print("ETL process completed successfully")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
