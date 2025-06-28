{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
    pkgs.nodePackages.typescript
    pkgs.nodePackages.typescript-language-server
    pkgs.python310Packages.pip
    pkgs.python310Packages.setuptools
    pkgs.sqlite
    pkgs.curl
    pkgs.git
  ];
  
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.glib
      pkgs.xorg.libX11
      pkgs.xorg.libXext
      pkgs.xorg.libXtst
      pkgs.xorg.libXi
      pkgs.xorg.libXrandr
      pkgs.xorg.libXcursor
      pkgs.libffi
      pkgs.openssl
    ];
    PYTHONPATH = "/home/runner/financial-planner-ai-agent";
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.glib
      pkgs.xorg.libX11
      pkgs.xorg.libXext
      pkgs.xorg.libXtst
      pkgs.xorg.libXi
      pkgs.xorg.libXrandr
      pkgs.xorg.libXcursor
      pkgs.libffi
      pkgs.openssl
    ];
  };
}
