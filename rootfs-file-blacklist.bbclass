# Search for blacklisted files deployed in a root filesystem, as defined by
# their name or type (according to the program 'file').
#
# SPDX-License-Identifier: MIT
# Author: Jon Szymaniak <jon.szymaniak.foss@gmail.com>

# Case-insensitive and semicolon-delimited list of filenames to blacklist.
# Glob-style wildcards (e.g. *.pem) are permitted.
BLACKLISTED_FILE_NAMES ?= ""

# Case insensitive and semicolon-delimited list of file types,
# as defined by the output of the "file" program
BLACKLISTED_FILE_TYPES ?= ""

python find_blacklisted_files() {
    from fnmatch import fnmatch

    type_blacklist = set()
    name_blacklist = set()
    glob_blacklist = []

    for entry in d.getVar('BLACKLISTED_FILE_NAMES').split(';'):
        entry = entry.strip().lower()
        if len(entry) == 0:
            continue
        elif '*' in entry:
            glob_blacklist.append(entry)
        else:
            name_blacklist.add(entry)

    for entry in d.getVar('BLACKLISTED_FILE_TYPES').split(';'):
        entry = entry.strip().lower()
        if len(entry):
            type_blacklist.add(entry)

    rootfs = d.getVar('IMAGE_ROOTFS')
    for root, dirs, files in os.walk(rootfs):
        for f in files:
            curr_path = os.path.join(root, f)
            dest_path = os.path.join(root[len(rootfs):], f)
            f = f.lower()

            if f in name_blacklist or any(fnmatch(f, g) for g in glob_blacklist):
                bb.warn('Blacklisted file (name) in rootfs: ' + dest_path)
            else:
                output, err = bb.process.run('file -b ' + curr_path)
                if any(t in output.lower() for t in type_blacklist):
                    bb.warn('Blacklisted file (type) in rootfs: ' + dest_path)
}

ROOTFS_POSTPROCESS_COMMAND += "find_blacklisted_files;"
DEPENDS += "file-native"
