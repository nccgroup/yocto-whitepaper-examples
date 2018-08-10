This repository contains example code included in NCC Group's *Improving Your Embedded Linux Security Posture with Yocto* whitepaper.

* The [dep-subgraph] Python script is discussed in Section 2.2 of the paper. This demonstrates one way to visualize a selected subset of package dependency information included in [Build History] output.
* The [rootfs-file-blacklist] and [symbol-blacklist] [BitBake] classes are basic examples showing how one can integrate both per-image and per-recipe QA checks into build processes. These are discussed in Section 3.3 of the paper.


[dep-subgraph]: ./dep-subgraph.py
[rootfs-file-blacklist]: ./rootfs-file-blacklist.bbclass
[symbol-blacklist]: ./symbol-blacklist.bbclass
[Build History]: https://www.yoctoproject.org/docs/2.5/dev-manual/dev-manual.html#maintaining-build-output-quality
[BitBake]: https://www.yoctoproject.org/docs/current/bitbake-user-manual/bitbake-user-manual.html
