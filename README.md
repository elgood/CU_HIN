# CU_HIN
Heterogeneous Information Network for CU 

## Installing

Clone the repo and set up a virtual environment:

    git clone https://github.com/elgood/CU_HIN.git
    cd CU_HIN
    virtualenv --python python3 .virtualenv
    source .virtualenv/bin/activate
    pip install -r requirements.txt

## Running

    python src/hin.py --dns_files <log file> \
                      --netflow_files <netflow v5 file>

Type *--help* for more options.
