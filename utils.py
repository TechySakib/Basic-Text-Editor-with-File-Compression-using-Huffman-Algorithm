"""General helper functions for formatting messages and small shared tasks."""


def format_compression_message(result: dict[str, float]) -> str:
    original_size = result["original_size"]
    compressed_size = result["compressed_size"]
    ratio = result["ratio"]
    return (
        "Compression successful.\n\n"
        f"Original size: {original_size} bytes\n"
        f"Compressed size: {compressed_size} bytes\n"
        f"Compression ratio: {ratio:.2f}"
    )
