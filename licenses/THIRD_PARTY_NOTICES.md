# ALLEN third-party notices for the Windows offline bundle

The distribution bundle must include the original notices for the exact versions shipped. This inventory is not a substitute for reviewing every transitive dependency in the final SBOM.

- **llama.cpp / ggml runtime**: MIT. Source project: <https://github.com/ggml-org/llama.cpp>. Include `MIT-llama.cpp.txt` with every distributed runtime.
- **LLVM OpenMP**: the WinGet llama.cpp package contains `LICENSE-LLVM-OpenMP`; retain that file beside the redistributed runtime.
- **Qwen3.5-0.8B-Q8_0 GGUF**: Apache License 2.0 according to the model repository. Include `Apache-2.0.txt` in the model package and preserve the model attribution.
- **Python runtime and Python dependencies**: the Nuitka standalone distributions bundle CPython and third-party modules. Generate/review an SBOM and copy each included project's license text into this directory before an institutional release.
- **Inno Setup**: build-time tool only; its compiler is not part of the client package. Check the official commercial-use terms for the organization and release context before distributing a product built with it.

## Exact runtime/model tested on the development PC

- llama.cpp: `0.4.1-dev (build 11026, commit b49650adb)` (WinGet package), CPU-oriented server plus DLLs copied from the same package.
- Qwen GGUF: `ggml-org/Qwen3.5-0.8B-GGUF`, `Qwen3.5-0.8B-Q8_0.gguf`; the tested local file was 833,592,096 bytes.
