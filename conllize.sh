cd ../WiFiNE_original/FineEntity/
for file in *
do
    cd ../../src
    echo "CoNLLizing $file..."
    python conllize.py -a $file -o $file
    cd ../WiFiNE_original/FineEntity/
done