# pillow-manylinux2014

Rebuilds [Pillow](https://github.com/python-pillow/Pillow) wheels for **glibc 2.17**
(`manylinux2014` / `manylinux_2_17`, i.e. RHEL/CentOS 7) for x86_64.

Upstream stopped publishing these in 12.3.0
([python-pillow/Pillow#9528](https://github.com/python-pillow/Pillow/pull/9528)),
as a platform-support decision rather than a technical one. 12.2.0 is the last
upstream release with a glibc 2.17 wheel. This repo re-enables the build with
Pillow's own tooling, so the bundled libjpeg-turbo, libtiff, libwebp, freetype,
etc. are the same current versions upstream ships in its other wheels.

## Building

Actions → *Build Pillow manylinux2014 wheels* → *Run workflow*. Inputs:

- `pillow_version` — upstream git tag, e.g. `13.0.0`
- `build` — cibuildwheel selector, default `cp311-manylinux_x86_64 cp312-manylinux_x86_64`
- `publish` — attach wheels and `SHA256SUMS` to a GitHub Release named after the version

The job checks out the upstream tag, applies `patches/`, runs cibuildwheel with
`CIBW_MANYLINUX_X86_64_IMAGE=manylinux2014` (everything else comes from
Pillow's `pyproject.toml`), runs Pillow's own test suite inside the build
container, then smoke-tests the wheel with a uv-managed Python in a glibc 2.17
container. Expect 20–40 minutes.

## Consuming

Pin the exact wheel in `requirements.txt`:

```
Pillow @ https://github.com/condense/pillow-manylinux2014/releases/download/13.0.0/pillow-13.0.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl --hash=sha256:<from SHA256SUMS>
```

pip (and the IMAS Ansible deploy, which just runs `pip install -r`) handles the
URL form natively. The repo must stay public, or the servers need a token.

The wheel is specific to the CPython minor version in its tag. If the deploy's
`uv_python_version` changes, build (and pin) the matching wheel.

## Maintenance

- **Each Pillow release**: run the workflow with the new version, update the
  pin. Check the upstream changelog for security fixes; that's the whole point.
- **`patches/`** edits `wheels-dependencies.sh` only: it reverts the
  manylinux2014-specific libavif hunk of #9528, and adds `-lm` to
  libjpeg-turbo's executable link flags (3.2+ bundles libspng for its CLI
  tools, whose static link fails on glibc 2.17 without it). If a future
  release changes that file the patch will stop applying; regenerate it.
- **This buys time, not a future.** The manylinux2014 image is EOL (still
  published as of Oct 2026), and upstream dependencies will eventually need a
  newer toolchain than CentOS 7 has — 12.x already special-cased zlib-ng on
  manylinux2014 aarch64. When the build breaks on a dependency, that's the
  signal to stop patching and move the hosts to a newer OS.
