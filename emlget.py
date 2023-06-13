#!/usr/bin/python
import argparse
import os
import pathlib
import requests
import urllib
import zipfile


def download_eml_zips(base_url, destination_dir=None):
    """
    Downloads the all EML ZIPs corresponding to the given `base_url` and places
    them in the given `destination_dir`.
    """
    election_name = base_url.split("_")[-1]
    if destination_dir is None:
        current_dirpath = pathlib.Path().resolve()
        destination_dir = os.path.join(current_dirpath, election_name)

    urls = [f"{base_url}_deel_{i}" for i in range(1, 4)]
    # Find all hosted ZIP files and download them
    i = 1
    while True:
        # Determine if ZIP number i exists first
        url = f"{base_url}_deel_{i}.zip"
        if not url_exists(url):
            break

        print(f"[*] Downloading ZIP file from {url}")
        urllib.request.urlretrieve(
            url,
            os.path.join(destination_dir, f"{election_name}_{i}.zip")
        )

        i += 1

    print("[*] Finished downloading EML ZIPs.")


def unzip_eml_zips(zips_dir=None):
    """
    Unzips all ZIP files found in `zips_dir` to that same directory.
    """
    print(f"[*] Unzipping all files in {zips_dir}...")

    for filename in os.listdir(zips_dir):
        if file_is_zipfile(filename):
            full_path = os.path.join(zips_dir, filename)
            print(f"[*] Unzipping {full_path}...")

            with zipfile.ZipFile(full_path, 'r') as f:
                f.extractall(zips_dir)


def delete_zips(zips_dir):
    """
    Deletes all ZIP files found in `zips_dir`.
    """
    print(f"[*] Deleting all ZIP files in {zips_dir}...")

    for filename in os.listdir(zips_dir):
        if file_is_zipfile(filename):
            os.remove(os.path.join(zips_dir, filename))


def url_exists(url):
    """
    Determines and reports whether the given `url` exists by checking the HTTP
    status code we receive after an HTTP HEAD request.
    """
    r = requests.get(url)
    if r.ok:
        print(f"[*] URL {url} exists!")
    else:
        print(f"[*] URL {url} returned status code {r.status_code}.")

    return r.ok


def file_is_zipfile(filename):
    """
    Determines whether the given `filename` is a ZIP file based on its file
    extension.
    """
    return os.path.splitext(filename)[1] == ".zip"


def parse_args():
    """
    Parses the given command line arguments to determine where and how the
    EML files should be downloaded and extracted.
    """
    parser = argparse.ArgumentParser(
        prog="emlget", description="Instantly download and structure EML files from data.overheid.nl."
    )

    parser.add_argument("base_url", metavar="base_url", type=str,
        help="The base part of the EML ZIP download URL before \"_deel_n.zip\"")
    parser.add_argument("-d", "--destination_dir", type=str,
        help="The directory in which the resulting EML files or constituency directories will be stored")
    parser.add_argument("-s", "--segregate_dirs", action="store_true",
        help="If set, the \"EML_bestanden_deel_n\" subdirectories will not be merged.")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    download_eml_zips(args.base_url, args.destination_dir)
    unzip_eml_zips(args.destination_dir)
    delete_zips(args.destination_dir)
