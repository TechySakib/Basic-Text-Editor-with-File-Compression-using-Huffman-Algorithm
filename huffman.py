import json
import os
import heapq
from dataclasses import dataclass


@dataclass
class HuffmanNode:
    """Node used in the Huffman tree."""

    char: str | None = None
    freq: int = 0
    left: "HuffmanNode | None" = None
    right: "HuffmanNode | None" = None

    def __lt__(self, other: "HuffmanNode") -> bool:
        return self.freq < other.freq


class HuffmanCoding:
    """Handles compression and decompression using Huffman coding."""

    HEADER_SEPARATOR = b"\n===HUFFMAN_HEADER_END===\n"

    def __init__(self) -> None:
        self.codes: dict[str, str] = {}
        self.reverse_codes: dict[str, str] = {}

    def build_frequency_table(self, text: str) -> dict[str, int]:
        frequency: dict[str, int] = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        return frequency

    def build_heap(self, frequency: dict[str, int]) -> list[HuffmanNode]:
        heap: list[HuffmanNode] = []
        for char, freq in frequency.items():
            heapq.heappush(heap, HuffmanNode(char=char, freq=freq))
        return heap

    def build_huffman_tree(self, heap: list[HuffmanNode]) -> HuffmanNode | None:
        if not heap:
            return None

        if len(heap) == 1:
            only_node = heapq.heappop(heap)
            root = HuffmanNode(freq=only_node.freq, left=only_node)
            return root

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)

        return heapq.heappop(heap)

    def generate_codes(self, root: HuffmanNode | None) -> None:
        self.codes = {}
        self.reverse_codes = {}

        def walk(node: HuffmanNode | None, current_code: str) -> None:
            if node is None:
                return

            if node.char is not None:
                if current_code == "":
                    current_code = "0"
                self.codes[node.char] = current_code
                self.reverse_codes[current_code] = node.char
                return

            walk(node.left, current_code + "0")
            walk(node.right, current_code + "1")

        walk(root, "")

    def encode_text(self, text: str) -> str:
        return "".join(self.codes[char] for char in text)

    def pad_encoded_text(self, encoded_text: str) -> tuple[str, int]:
        extra_padding = (8 - len(encoded_text) % 8) % 8
        return encoded_text + ("0" * extra_padding), extra_padding

    def binary_string_to_bytes(self, binary_string: str) -> bytes:
        if len(binary_string) % 8 != 0:
            raise ValueError("Binary string length must be a multiple of 8.")

        byte_array = bytearray()
        for index in range(0, len(binary_string), 8):
            byte_array.append(int(binary_string[index:index + 8], 2))
        return bytes(byte_array)

    def bytes_to_binary_string(self, byte_data: bytes) -> str:
        return "".join(f"{byte:08b}" for byte in byte_data)

    def rebuild_tree_from_frequency(self, frequency: dict[str, int]) -> HuffmanNode | None:
        return self.build_huffman_tree(self.build_heap(frequency))

    def decode_text(self, binary_string: str, root: HuffmanNode | None) -> str:
        if root is None:
            return ""

        decoded_chars: list[str] = []
        current = root
        for bit in binary_string:
            current = current.left if bit == "0" else current.right
            if current and current.char is not None:
                decoded_chars.append(current.char)
                current = root
        return "".join(decoded_chars)

    def compress_file(self, input_path: str, output_path: str) -> dict[str, float]:
        with open(input_path, "r", encoding="utf-8") as file:
            text = file.read()

        if text == "":
            raise ValueError("Cannot compress an empty file.")

        frequency = self.build_frequency_table(text)
        heap = self.build_heap(frequency)
        root = self.build_huffman_tree(heap)
        self.generate_codes(root)

        encoded_text = self.encode_text(text)
        padded_text, padding = self.pad_encoded_text(encoded_text)
        compressed_bytes = self.binary_string_to_bytes(padded_text)

        header = {
            "original_filename": os.path.basename(input_path),
            "frequency": frequency,
            "padding": padding,
        }
        header_bytes = json.dumps(header, ensure_ascii=False).encode("utf-8")

        with open(output_path, "wb") as out_file:
            out_file.write(header_bytes)
            out_file.write(self.HEADER_SEPARATOR)
            out_file.write(compressed_bytes)

        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        return {
            "original_size": original_size,
            "compressed_size": compressed_size,
            "ratio": (compressed_size / original_size) if original_size else 0,
        }

    def decompress_file(self, input_path: str, output_path: str) -> dict[str, int]:
        with open(input_path, "rb") as file:
            data = file.read()

        separator_index = data.find(self.HEADER_SEPARATOR)
        if separator_index == -1:
            raise ValueError("Invalid compressed file format: header separator not found.")

        header_bytes = data[:separator_index]
        payload = data[separator_index + len(self.HEADER_SEPARATOR):]

        try:
            header = json.loads(header_bytes.decode("utf-8"))
        except Exception as exc:
            raise ValueError("Failed to read compressed file header.") from exc

        if "frequency" not in header or "padding" not in header:
            raise ValueError("Invalid compressed file format: missing required metadata.")

        frequency = header["frequency"]
        padding = header["padding"]

        root = self.rebuild_tree_from_frequency(frequency)
        binary_string = self.bytes_to_binary_string(payload)
        if padding > 0:
            binary_string = binary_string[:-padding]

        decoded_text = self.decode_text(binary_string, root)
        with open(output_path, "w", encoding="utf-8") as out_file:
            out_file.write(decoded_text)

        return {"restored_size": os.path.getsize(output_path)}
