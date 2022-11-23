{ pkgs }: {
    deps = [
        pkgs.unzip
        pkgs.python310Packages.setuptools
        pkgs.python310Packages.pip
        pkgs.python310Packages.virtualenv
        pkgs.python310
    ];
}