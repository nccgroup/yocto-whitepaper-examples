# Blacklist symbols within applications and libraries
#
# SPDX-License-Identifier: MIT
# Author: Jon Szymaniak <jon.szymaniak.foss@gmail.com>

# Space-delimited list of blacklisted symbol names
BLACKLISTED_SYMBOLS ?= "\
    atoi atol atof \
    gets \
    strcpy stpcpy strcat \
    sprintf vsprintf \
"

def is_elf(f):
    out, err = bb.process.run('file -b ' + f)
    return 'ELF' in out

def check_file(d, file_path):
    if not is_elf(file_path):
        return

    readelf = d.getVar('READELF')
    out, err = bb.process.run(readelf + ' --syms ' + file_path)
    for sym in d.getVar('BLACKLISTED_SYMBOLS').split():
        if sym in out:
            msg = 'Blacklisted symbol "{:s}" present in {:s}'
            bb.warn(msg.format(sym, file_path))

python do_find_blacklisted_symbols() {
    install_dir = d.getVar('D')
    for root, dirs, files in os.walk(install_dir):
        for f in files:
            check_file(d, os.path.join(root, f))
}

addtask do_find_blacklisted_symbols after do_install before do_package 
