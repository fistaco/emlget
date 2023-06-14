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
    # Generate the destination directory's name if the user doesn't provide one
    election_name = base_url.split("_")[-1]
    if destination_dir is None:
        current_dirpath = pathlib.Path().resolve()
        destination_dir = os.path.join(current_dirpath, election_name)

    # Create the destination directory if necessary
    if not os.path.isdir(destination_dir):
        os.mkdir(destination_dir)

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


def merge_subdirectories(main_dir):
    """
    Merges all the subdirectories in `main_dir` that may have been extracted
    from the segmented ZIP files, e.g., merge the contents of directories
    "EML_bestanden_TK2021_deel_1", "EML_bestanden_TK2021_deel_2", and
    "EML_bestanden_TK2021_deel_3".

    Note that, in order to avoid merging irrelevant directories, this method
    will only merge directories with names that start with "EML" and end with a
    digit.
    """
    main_dir_abs = os.path.abspath(main_dir)
    subdirs = next(os.walk(main_dir))[1]
    print(f"Found subdirectories: {', '.join(subdirs)}")

    # Find all subsubdirectories with matching names, move their files to a
    # new, unifying subsubdirectory, and place that dir in the main subdir.
    for subdir in subdirs:  # Iterates over "EML_bestanden_..._i"
        subdir_abs = os.path.join(main_dir_abs, subdir)
        print(f"[*] Moving files from {subdir}")

        files = os.listdir(subdir_abs)
        for filename in files:
            filepath_abs = os.path.join(subdir_abs, filename)  # Can be a dir

            # Move/merge all subsubdirectory contents
            if os.path.isdir(filepath_abs):  # Likely constituency/municipality
                new_subdir = os.path.join(main_dir_abs, filename)
                print(f"[*] Moving files from {filepath_abs} to {new_subdir}")

                if not os.path.exists(new_subdir):
                    os.mkdir(new_subdir)

                for eml_filename in os.listdir(filepath_abs):
                    eml_file_abspath = os.path.join(filepath_abs, eml_filename)
                    os.rename(
                        eml_file_abspath,
                        os.path.join(new_subdir, eml_filename)
                    )
            # Move normal files directly to main_dir
            else:
                dest = os.path.join(main_dir, filename)
                print(f"[*] Moving {filepath_abs} to {dest}")

                os.rename(filepath_abs, dest)

        # Remove the subdirectory, as it should now be empty
        try:
            os.rmdir(subdir_abs)
        except OSError:
            print(f"[!] Could not delete directory {subdir} because it is not empty.")


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
    if not args.segregate_dirs:
        merge_subdirectories(args.destination_dir)
