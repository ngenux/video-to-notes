import subprocess

def convert_md_to_pdf(md_file_path, destination_path):
    """
    Convert Markdown file to PDF using Pandoc.

    Args:
    md_file_path (str): Path to the Markdown file.
    destination_path (str): Path where the PDF will be saved.
    """

    process = subprocess.Popen(
        ['pandoc', md_file_path, '-o', destination_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(
            'Pandoc died with exit code "%s" during conversion: %s' % (process.returncode, stderr.decode())
        )
    else:
        print('PDF successfully created as', destination_path)

# # Example usage
# md_file_path = r'C:\Users\MohammedKareemKhan\Downloads\algebra_md.md'
# destination_path = r'C:\Users\MohammedKareemKhan\Desktop\project\video-to-notes\transcript_in_pdf\Green Revolution.pdf'

# convert_md_to_pdf(md_file_path, destination_path)
