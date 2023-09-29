"""Title: EmbedFonts Plugin for IS.MUNI-sync

Description: The EmbedFonts plugin automatically embeds fonts in downloaded PDF
files to ensure visual consistency across different systems.

Requirements:
- Ghostscript installed and available in the system's PATH.
- pdffonts tool installed and available in the system's PATH.

Sample Configuration:
[Plugins]
EmbedFonts = PV079

Place this configuration under the [Plugins] section in your config.ini file,
and specify the channels you want this plugin to run on.

"""
import subprocess
import logging
import os

class EmbedFonts:
    def on_file_downloaded(self, file_path):
        if not file_path.endswith('.pdf'):
            return

        logging.info(f"Checking fonts in {file_path}")
        check_command = ['pdffonts', file_path]
        result = subprocess.run(check_command, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error checking fonts in {file_path}: {result.stderr}")
        else:
            logging.debug(result.stdout)

        if 'no' in result.stdout.split():
            logging.info(f"Running EmbedFonts plugin on {file_path}")
            embed_command = [
                'gs',
                '-o', 'tmp.pdf',
                '-sDEVICE=pdfwrite',
                '-dEmbedAllFonts=true',
                file_path
            ]
            result = subprocess.run(embed_command, capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f"Error embedding fonts in {file_path}: {result.stderr}")
            else:
                os.rename('tmp.pdf', file_path)
                logging.info(f"Embedded fonts in {file_path}")

            logging.debug(result.stdout)
        else:
            logging.info(f"All fonts are already embedded in {file_path}")
