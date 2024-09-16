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

    output_df = gene_data.loc[
        :, ["gene_id", "feature", "gene_biotype", "seqname", "source"]
    ]

    return output_df


def main():
    parser = argparse.ArgumentParser(description="tbd")
    parser.add_argument("--species", type=str, help="Ensembl species name")
    parser.add_argument("--release", type=int, help="Ensembl release version")
    args = parser.parse_args()

    download_gtf_files(args.release, args.species)
    unzip_gtf_files()

    df = read_gtf_file(
        os.path.join(temp_download_folder, "Cajanus_cajan.C.cajan_V1.0.56.gtf")
    )

    df = extract_key_attributes(df)

    df = transform_data(df)

    df.to_csv("test.csv", sep="\t", header=True, index=False)


if __name__ == "__main__":
    main()
