#!/bin/bash

# Function to display usage instructions
usage() {
    echo "Usage: $0 input.pdf page_number 'llx lly urx ury' output_format output_file"
    echo "Example: $0 input.pdf 1 '100 100 500 500' jpg output.jpg"
    echo "output_format should be either 'jpg' or 'png'."
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 5 ]; then
    echo "Error: Invalid number of arguments."
    usage
fi

input_pdf=$1
page_number=$2
bbox=$3
output_format=$4  # either "jpg" or "png"
output_file=$5

# Check if input PDF exists
if [ ! -f "$input_pdf" ]; then
    echo "Error: Input PDF file '$input_pdf' does not exist."
    usage
fi

# Check if page number is a positive integer
if ! [[ "$page_number" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: Page number '$page_number' is not a valid positive integer."
    usage
fi

# Check if bbox is correctly formatted
if ! [[ "$bbox" =~ ^[0-9]+[[:space:]][0-9]+[[:space:]][0-9]+[[:space:]][0-9]+$ ]]; then
    echo "Error: Bounding box '$bbox' is not correctly formatted."
    usage
fi

# Check if the output format is valid
if [[ "$output_format" != "jpg" && "$output_format" != "png" ]]; then
    echo "Error: Invalid output format. Please specify either 'jpg' or 'png'."
    usage
fi

# Check if the output file has the correct extension
if [[ "$output_file" != *.$output_format ]]; then
    echo "Error: Output file name must have the extension .$output_format."
    usage
fi

# Extract the specific page
pdftk "$input_pdf" cat "$page_number" output temp_slide.pdf
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract page $page_number from $input_pdf."
    exit 1
fi

# Crop the extracted page
pdfcrop --bbox "$bbox" temp_slide.pdf cropped_slide.pdf
if [ $? -ne 0 ]; then
    echo "Error: Failed to crop the page with bounding box $bbox."
    exit 1
fi

# Convert the cropped PDF to the specified image format using pdftoppm
if [ "$output_format" == "jpg" ]; then
    pdftoppm cropped_slide.pdf cropped_slide -jpeg -singlefile
    if [ $? -ne 0 ]; then
        echo "Error: pdftoppm failed to convert PDF to JPEG."
        exit 1
    fi
    mv cropped_slide.jpg "$output_file"
else
    pdftoppm cropped_slide.pdf cropped_slide -png -singlefile
    if [ $? -ne 0 ]; then
        echo "Error: pdftoppm failed to convert PDF to PNG."
        exit 1
    fi
    mv cropped_slide.png "$output_file"
fi

# Clean up temporary files
rm temp_slide.pdf cropped_slide.pdf

echo "Cropped slide saved as $output_file"
