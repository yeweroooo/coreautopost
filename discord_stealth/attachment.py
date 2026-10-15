import mimetypes
import os
from curl_cffi import requests

from .constants import DISCORD_API_BASE


class AttachmentUploader:
    """Modul uploader attachment Discord via Google Cloud Storage pre-signed URL."""

    @staticmethod
    def prepare_file_descriptor(item: str | tuple[str, bytes, str | None], index: int) -> dict:
        """Standardisasi file descriptor baik dari file path maupun in-memory bytes."""
        if isinstance(item, str):
            filename = os.path.basename(item)
            with open(item, "rb") as f:
                data = f.read()
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        elif isinstance(item, (tuple, list)):
            filename = item[0]
            data = item[1]
            content_type = item[2] if len(item) > 2 and item[2] else (mimetypes.guess_type(filename)[0] or "application/octet-stream")
        else:
            raise ValueError(f"Tipe file tidak didukung: {type(item)}")

        return {
            "id": str(index),
            "filename": filename,
            "file_size": len(data),
            "is_clip": False,
            "original_content_type": content_type,
            "_data": data,
        }

    @classmethod
    def upload_files(
        cls,
        http_session: requests.Session,
        channel_id: str,
        request_headers: dict[str, str],
        user_agent: str,
        files: list[str | tuple[str, bytes, str | None]],
        timeout: int = 30,
    ) -> list[dict]:
        """
        1. Request upload URL dari Discord API
        2. PUT raw data ke storage cloud
        3. Kembalikan list attachments yang siap disematkan pada pesan
        """
        descriptors = [cls.prepare_file_descriptor(item, idx) for idx, item in enumerate(files)]
        if not descriptors:
            return []

        req_url = f"{DISCORD_API_BASE}/channels/{channel_id}/attachments"
        req_payload = {
            "files": [
                {
                    "filename": d["filename"],
                    "file_size": d["file_size"],
                    "id": d["id"],
                    "is_clip": d["is_clip"],
                    "original_content_type": d["original_content_type"],
                }
                for d in descriptors
            ]
        }

        resp = http_session.post(req_url, headers=request_headers, json=req_payload, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"Gagal request upload URL dari Discord [{resp.status_code}]: {resp.text}")

        upload_plans = resp.json().get("attachments", [])

        put_headers = {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/octet-stream",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }

        final_attachments = []
        for idx, plan in enumerate(upload_plans):
            put_url = plan["upload_url"]
            uploaded_filename = plan["upload_filename"]
            raw_data = descriptors[idx]["_data"]

            put_resp = http_session.put(put_url, headers=put_headers, data=raw_data, timeout=timeout)
            if put_resp.status_code not in (200, 204):
                raise RuntimeError(
                    f"Gagal upload file {descriptors[idx]['filename']} ke storage [{put_resp.status_code}]"
                )

            final_attachments.append({
                "id": str(idx),
                "filename": descriptors[idx]["filename"],
                "uploaded_filename": uploaded_filename,
                "original_content_type": descriptors[idx]["original_content_type"],
            })

        return final_attachments
