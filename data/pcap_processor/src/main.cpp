#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <pcap.h>
#include <pybind11/embed.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

namespace py = pybind11;

struct FiveTuple {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t src_port;
    uint16_t dst_port;
    uint8_t protocol;

    bool operator==(const FiveTuple &other) const {
        return src_ip == other.src_ip && dst_ip == other.dst_ip &&
               src_port == other.src_port && dst_port == other.dst_port &&
               protocol == other.protocol;
    }

    std::string toByteArray() const {
        char buffer[13];
        memcpy(buffer, &src_ip, sizeof(src_ip));
        memcpy(buffer + 4, &dst_ip, sizeof(dst_ip));
        memcpy(buffer + 8, &src_port, sizeof(src_port));
        memcpy(buffer + 10, &dst_port, sizeof(dst_port));
        memcpy(buffer + 12, &protocol, sizeof(protocol));
        return std::string(buffer, 13);
    }
};

namespace std {
template <>
struct hash<FiveTuple> {
    size_t operator()(const FiveTuple &id) const {
        return hash<std::string>{}(id.toByteArray());
    }
};
}  // namespace std

struct PacketData {
    FiveTuple id;
    std::string header;
    uint32_t flow_size;
};

std::vector<PacketData> parse_pcap(const std::string &pcap_file,
                                   const std::string &link_layer_type) {
    std::vector<PacketData> packets;

    pcap_t *handle;
    char errbuf[PCAP_ERRBUF_SIZE];

    handle = pcap_open_offline(pcap_file.c_str(), errbuf);
    if (!handle) {
        std::cerr << "Error opening PCAP file: " << errbuf << std::endl;
        return packets;
    }

    int link_layer_len;
    if (link_layer_type == "None")
        link_layer_len = 0;
    else if (link_layer_type == "Ethernet")
        link_layer_len = sizeof(struct ether_header);
    else
        link_layer_len = sizeof(struct ether_header) + 4;

    struct pcap_pkthdr cap_header;
    const u_char *packet;

    while ((packet = pcap_next(handle, &cap_header)) != nullptr) {
        if (cap_header.caplen < (link_layer_len + sizeof(struct ip))) {
            continue;
        }

        if (link_layer_type == "Ethernet" || link_layer_type == "802.1Q") {
            const struct ether_header *eth_hdr =
                reinterpret_cast<const struct ether_header *>(packet);
            uint16_t ether_type = eth_hdr->ether_type;

            if (link_layer_type == "802.1Q") {
                if (ntohs(ether_type) != ETHERTYPE_VLAN) {
                    continue;
                }
                const uint16_t *ether_type_ptr =
                    reinterpret_cast<const uint16_t *>(packet + 16);
                ether_type = *ether_type_ptr;
            }

            if (ntohs(ether_type) != ETHERTYPE_IP) {
                continue;
            }
        }

        const struct ip *ip_header =
            reinterpret_cast<const struct ip *>(packet + link_layer_len);
        if (ip_header->ip_v != 4) {
            continue;
        }

        size_t ip_header_len = ip_header->ip_hl * 4;
        if (cap_header.caplen < link_layer_len + ip_header_len) {
            continue;
        }

        PacketData packet_data;
        packet_data.id.src_ip = ip_header->ip_src.s_addr;
        packet_data.id.dst_ip = ip_header->ip_dst.s_addr;
        packet_data.id.protocol = ip_header->ip_p;
        packet_data.id.src_port = 0;
        packet_data.id.dst_port = 0;

        const u_char *ip_start = packet + link_layer_len;

        if (ip_header->ip_p == IPPROTO_TCP) {
            if (cap_header.caplen <
                link_layer_len + ip_header_len + sizeof(struct tcphdr)) {
                continue;
            }
            const struct tcphdr *tcp_header =
                reinterpret_cast<const struct tcphdr *>(ip_start +
                                                        ip_header_len);
            packet_data.id.src_port = tcp_header->th_sport;
            packet_data.id.dst_port = tcp_header->th_dport;

            packet_data.header =
                std::string(reinterpret_cast<const char *>(ip_start),
                            ip_header_len + sizeof(struct tcphdr));

        } else if (ip_header->ip_p == IPPROTO_UDP) {
            if (cap_header.caplen <
                link_layer_len + ip_header_len + sizeof(struct udphdr)) {
                continue;
            }
            const struct udphdr *udp_header =
                reinterpret_cast<const struct udphdr *>(ip_start +
                                                        ip_header_len);
            packet_data.id.src_port = udp_header->uh_sport;
            packet_data.id.dst_port = udp_header->uh_dport;

            packet_data.header =
                std::string(reinterpret_cast<const char *>(ip_start),
                            ip_header_len + sizeof(struct udphdr));

        } else {
            packet_data.header = std::string(
                reinterpret_cast<const char *>(ip_start), ip_header_len);
        }

        if (packet_data.header.size() >= 20) {
            memset(&packet_data.header[12], 0, 8);
        }

        packets.push_back(packet_data);
    }

    pcap_close(handle);
    return packets;
}

void calcFlowSizes(std::vector<PacketData> &packets) {
    std::unordered_map<FiveTuple, uint32_t> flow_sizes;
    for (const auto &packet : packets) {
        flow_sizes[packet.id]++;
    }
    for (auto &packet : packets) {
        packet.flow_size = flow_sizes[packet.id];
    }
}

void save_to_npz(const std::vector<PacketData> &packets,
                 const std::string &npz_file) {
    py::scoped_interpreter guard{};
    py::module numpy = py::module::import("numpy");

    py::list id_list, header_list, flow_size_list;

    for (const auto &packet : packets) {
        id_list.append(py::bytes(packet.id.toByteArray()));
        header_list.append(py::bytes(packet.header));
        flow_size_list.append(packet.flow_size);
    }

    py::object id_array = numpy.attr("array")(id_list, py::dtype("object"));
    py::object header_array =
        numpy.attr("array")(header_list, py::dtype("object"));
    py::object flow_size_array = numpy.attr("array")(flow_size_list);

    py::dict data_dict;
    data_dict["id"] = id_array;
    data_dict["header"] = header_array;
    data_dict["flow_size"] = flow_size_array;

    numpy.attr("savez_compressed")(npz_file, **data_dict);
}

int main(int argc, char *argv[]) {
    if (argc < 3 || argc > 4) {
        std::cerr
            << "Usage: " << argv[0]
            << " <pcap_file> <npz_file> [link_layer_type=None|Ethernet|802.1Q]"
            << std::endl;
        return 1;
    }

    std::string pcap_file = argv[1];
    std::string npz_file = argv[2];
    std::string link_layer_type = (argc == 4) ? argv[3] : "None";

    if (link_layer_type != "None" && link_layer_type != "Ethernet" &&
        link_layer_type != "802.1Q") {
        std::cerr
            << "Invalid link_layer_type. Allowed values: None, Ethernet, 802.1Q"
            << std::endl;
        return 1;
    }

    auto packets = parse_pcap(pcap_file, link_layer_type);

    calcFlowSizes(packets);

    save_to_npz(packets, npz_file);

    return 0;
}
