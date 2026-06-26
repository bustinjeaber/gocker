import os
import sys
import requests

REGISTRY_URL = "https://registry-1.docker.io/v2"
AUTH_URL = "https://auth.docker.io/token"

def get_token(repo):
    payload = {
        "service": "registry.docker.io",
        "scope": f"repository:{repo}:pull"
    }
    r = requests.get(AUTH_URL, params=payload)
    if r.status_code != 200:
        print(f"[gkr] auth error: {r.status_code}")
        sys.exit(1)
    return r.json()["token"]

def pull_image(image_name, tag, images_dir):
    repo = f"library/{image_name}" if "/" not in image_name else image_name
    target_rootfs = images_dir / f"{image_name}_{tag}"

    if target_rootfs.exists():
        print(f"[gkr] {image_name}:{tag} is on a disk.")
        return target_rootfs

    print(f"[gkr] wait dockerhub {image_name}:{tag}...")
    token = get_token(repo)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.index.v1+json"
    }

    res = requests.get(f"{REGISTRY_URL}/{repo}/manifests/{tag}", headers=headers)
    if res.status_code != 200:
        print(f"[gkr] image doesnt exist: {res.status_code}")
        sys.exit(1)
    
    manifest = res.json()
    if "manifests" in manifest:
        arch_digest = None
        for m in manifest["manifests"]:
            if m.get("platform", {}).get("architecture") == "amd64":
                arch_digest = m["digest"]
                break
        if not arch_digest:
            arch_digest = manifest["manifests"][0]["digest"]
        res = requests.get(f"{REGISTRY_URL}/{repo}/manifests/{arch_digest}", headers=headers)
        manifest = res.json()
    layers = manifest.get("layers", [])
    if not layers:
        print("[gkr] manifest is empty")
        sys.exit(1)

    target_rootfs.mkdir(parents=True, exist_ok=True)

    for i, layer in enumerate(layers):
        digest = layer["digest"]
        print(f"[*] downloading [{i+1}/{len(layers)}]: {digest[:12]}...")
        
        blob_url = f"{REGISTRY_URL}/{repo}/blobs/{digest}"
        blob_res = requests.get(blob_url, headers={"Authorization": f"Bearer {token}"}, stream=True)
        
        tmp_tar = images_dir / f"tmp_{i}.tar.gz"
        with open(tmp_tar, "wb") as f:
            for chunk in blob_res.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        os.system(f"sudo tar -xf {tmp_tar} -C {target_rootfs}")
        tmp_tar.unlink()
    print(f"[gkr] rootfs : {target_rootfs}")
    return target_rootfs