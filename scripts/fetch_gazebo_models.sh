#!/usr/bin/env bash
set -euo pipefail

readonly MODEL_BASE_URL="http://models.gazebosim.org"
readonly CACHE_DIR="${GAZEBO_MODEL_CACHE_DIR:-${HOME}/.gazebo/models}"

fetch_model() {
    local name="$1"
    local mesh="$2"
    local checksum="$3"
    local destination="${CACHE_DIR}/${name}"

    if [[ -f "${destination}/${mesh}" ]]; then
        printf '%s is already cached in %s\n' "$name" "$destination"
        return
    fi
    if [[ -e "$destination" ]]; then
        printf 'incomplete model cache exists: %s\n' "$destination" >&2
        return 1
    fi

    local work_dir archive
    work_dir="$(mktemp -d)"
    archive="${work_dir}/${name}.tar.gz"
    trap 'rm -rf -- "$work_dir"' RETURN

    curl --fail --location --retry 3 --retry-all-errors \
        --output "$archive" "${MODEL_BASE_URL}/${name}/model.tar.gz"
    printf '%s  %s\n' "$checksum" "$archive" | sha256sum --check --status

    if ! tar -tzf "$archive" | awk -v root="${name}/" 'index($0, root) != 1 { exit 1 }'; then
        printf 'unexpected path in archive for model %s\n' "$name" >&2
        return 1
    fi

    tar -xzf "$archive" -C "$work_dir"
    [[ -f "${work_dir}/${name}/${mesh}" ]]
    mkdir -p "$CACHE_DIR"
    mv "${work_dir}/${name}" "$destination"
    printf 'cached %s in %s\n' "$name" "$destination"
}

fetch_model \
    cafe_table \
    meshes/cafe_table.dae \
    e2f28b26f8198074a94c46cda4dbe660b33f97cd41d3dbf44aae8f20ba425ad3
fetch_model \
    person_standing \
    meshes/standing.dae \
    a2a10dca146304ed61e3242d4f1cb02d7354e1f3115db07c4c0fc2c92e3d1ab6
