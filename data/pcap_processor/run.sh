#!/bin/bash

pcap_dir="../pcap"
npz_dir="../npz"

for pcap_file in "$pcap_dir"/*.pcap; do
    filename=$(basename "$pcap_file" .pcap)
    npz_file="$npz_dir/$filename.npz"

    if [ -f "$npz_file" ]; then
        echo "npz file exists: $npz_file"
        continue
    fi

    echo "processing $pcap_file -> $npz_file"
    ./build/pcap_processor "$pcap_file" "$npz_file" Ethernet
done
