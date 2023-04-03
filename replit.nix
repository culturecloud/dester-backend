{ pkgs }: {
    deps = [
        pkgs.unzip
        pkgs.rclone
        pkgs.python310
    ];
    env = {
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      # Neded for pandas / numpy
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      # Needed for pygame
      pkgs.glib
    ];
    PYTHONBIN = "${pkgs.python310}/bin/python3.10";
  };
}