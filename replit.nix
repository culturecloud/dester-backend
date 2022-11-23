{ pkgs }: {
    deps = [
        pkgs.unzip
        pkgs.gcc48
        pkgs.python310Packages.setuptools
        pkgs.python310Packages.pip
        pkgs.python310Packages.virtualenv
        pkgs.python310
    ];
}