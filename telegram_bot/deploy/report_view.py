"""Index inline Allure data so a sandboxed viewer can read it on demand."""
import json
import mmap
import os
import re
from pathlib import Path

BLOCK = 256 * 1024
VIEW_BUDGET = 16 * 1024 * 1024
BRIDGE = Path(__file__).with_name("report-bridge.js")
KEY = rb'("(?:data|widgets)/[^"\\<>\r\n]{1,512}")'

# Both formats store resources as base64 literals without escaped quotes.
PACKED_ENTRY = re.compile(rb'<script>window\.allureReportData\[' + KEY + rb'\]="')
PACKED_END = b'";</script>\n'
PACKED_READY = b'<script>window.allureReportDataReady=true;</script>'
LEGACY_ARRAY = b"Promise.allSettled(["
LEGACY_ENTRY = re.compile(rb'd\(' + KEY + rb',"')


def build_view(source, destination):
    """Return False for unknown standalone HTML. Never copy an attachment into RAM."""
    stat = source.stat()
    if not stat.st_size:
        return False
    with source.open("rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as src:
        src.madvise(mmap.MADV_SEQUENTIAL)
        first = src.find(b"\n<script>window.allureReportData[", 0, BLOCK)
        packed = first >= 0 and b"window.allureReportData=Object.create(null)" in src[:first]
        if packed:
            header_end = first + 1
            pos = header_end
            entry = PACKED_ENTRY
        else:
            header_end = src.find(LEGACY_ARRAY + b'd("widgets/', 0, VIEW_BUDGET)
            if header_end < 0 or src.find(b"window.allureReportDataReady = false;", 0, header_end) < 0:
                return False
            pos = header_end + len(LEGACY_ARRAY)
            entry = LEGACY_ENTRY

        with destination.open("xb") as out:
            os.posix_fallocate(out.fileno(), 0, VIEW_BUDGET)

            def write(data):
                if out.tell() + len(data) > VIEW_BUDGET:
                    raise ValueError("Allure viewer exceeds its disk reservation")
                out.write(data)

            write(src[:header_end])
            if packed:
                write(b"<script>")
            write(BRIDGE.read_bytes())
            # Nginx's static-file ETag binds the byte offsets to this upload.
            etag = f'"{int(stat.st_mtime):x}-{stat.st_size:x}"'
            write(f"\nconst reportETag = {json.dumps(etag)};\n".encode())
            while match := entry.match(src, pos):
                start = match.end()
                end = src.find(b'"', start)
                terminator = PACKED_END if packed else b'")'
                if end < 0 or src[end:end + len(terminator)] != terminator:
                    raise ValueError("Incomplete Allure base64 value")
                write(b"deferFile(" + match[1] + f",{start},{end - start});\n".encode())
                pos = end + len(terminator)
                if not packed and src[pos:pos + 1] == b",":
                    pos += 1

            if packed and src[pos:pos + len(PACKED_READY)] == PACKED_READY:
                write(b"</script>\n")
            elif not packed and src[pos:pos + 2] == b"])":
                pos = src.find(b"</script>", pos, pos + BLOCK)
                if pos < 0:
                    raise ValueError("Incomplete legacy Allure report")
                write(b"window.allureReportDataReady = true;\n")
            else:
                raise ValueError("Unrecognized packed Allure data entry")
            while pos < len(src):
                write(src[pos:pos + BLOCK])
                pos += BLOCK
            out.truncate(out.tell())
    return True
