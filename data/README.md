### Overview

- `pcap/`: This folder stores the original `.pcap` files used in the datasets. You can place your own `.pcap` files in this directory.
- `npz/`: This folder stores the `.npz` files generated from the original `.pcap` files. We include two sample MAWI dataset files—one for training and one for testing.
- `pcap_processor/`: This folder contains the C++/Pybind11-based script used to process `.pcap` files and produce `.npz` files. We implemented this in C++ to overcome Python’s limited throughput when dealing with large packet captures.

### Compiling the Processor

To build the `pcap_processor` tool, run:

```
cd pcap_processor
mkdir build
cd build
cmake ..
make
```

### Running the Processor

Execute the processor with:

```
./pcap_processor <pcap_file> <npz_file> [link_layer_type=None|Ethernet|802.1Q]
```

where:

- `<pcap_file>` is your input `.pcap` file.
- `<npz_file>` is the output `.npz` file.
- `link_layer_type` is an optional parameter that can be set to `None`, `Ethernet`, or `802.1Q` depending on the dataset.

Below is an example of how we set `link_layer_type` for three datasets mentioned in our paper:

| Dataset | `link_layer_type` |
| ------- | ----------------- |
| CAIDA   | `None`            |
| MAWI    | `Ethernet`        |
| IMC DC  | `802.1Q`          |

### Processing Multiple PCAP Files

We also provide a `run.sh` script that automatically processes all `.pcap` files in a given folder using the same parameters. Simply update the script to point to your desired input folder and run:

```
./run.sh
```

This will generate the corresponding `.npz` files in the location you specify.