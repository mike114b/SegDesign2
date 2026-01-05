#!/bin/bash

# ===================== Configuration Parameters (Modify as Needed) =====================
# Download URL
DOWNLOAD_URL="https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz"
# Specified save path (Modify to your desired path, e.g., /home/user/data)
TARGET_DIR="./database"
# Saved compressed file name (defaults to original name, customizable)
COMPRESSED_FILE_NAME="uniref100.fasta.gz"
# ======================================================================================

# Combine the full path of the compressed file
COMPRESSED_FILE="${TARGET_DIR}/${COMPRESSED_FILE_NAME}"
# Derive the decompressed file name (remove .gz suffix)
DECOMPRESSED_FILE="${COMPRESSED_FILE%.gz}"

# 1. Check and create target directory if not exists
if [ ! -d "${TARGET_DIR}" ]; then
    echo "Target directory does not exist, creating now: ${TARGET_DIR}"
    mkdir -p "${TARGET_DIR}"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create directory ${TARGET_DIR}, please check permissions!"
        exit 1
    fi
fi

# 2. Check for download tools (prefer wget, fallback to curl if unavailable)
if command -v wget &> /dev/null; then
    echo "Downloading with wget..."
    wget -c "${DOWNLOAD_URL}" -O "${COMPRESSED_FILE}"
elif command -v curl &> /dev/null; then
    echo "Downloading with curl..."
    curl -C - -L -o "${COMPRESSED_FILE}" "${DOWNLOAD_URL}"
else
    echo "Error: Neither wget nor curl found, please install one first!"
    exit 1
fi

# 3. Verify download success
if [ $? -ne 0 ]; then
    echo "Error: Download failed!"
    exit 1
fi
echo "Download successful! Compressed file path: ${COMPRESSED_FILE}"

# 4. Check for decompression tool (gunzip for .gz files)
if ! command -v gunzip &> /dev/null; then
    echo "Error: gunzip not found, please install it first!"
    exit 1
fi

# 5. Decompress the .gz file (decompressed file in the same directory)
echo "Starting decompression..."
gunzip "${COMPRESSED_FILE}"
if [ $? -eq 0 ]; then
    echo "Decompression successful! Decompressed file path: ${DECOMPRESSED_FILE}"
    echo "Compressed file has been deleted automatically."
else
    echo "Error: Decompression failed! Compressed file retained."
    exit 1
fi

exit 0