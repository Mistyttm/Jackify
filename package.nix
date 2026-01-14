{ lib
, buildPythonApplication
, setuptools
, wheel
, pyside6
, psutil
, requests
, tqdm
, pycryptodome
, pyyaml
, vdf
, packaging
}:

let
  # Extract version from __init__.py
  versionLine = builtins.head (builtins.filter 
    (line: lib.hasPrefix "__version__" line)
    (lib.splitString "\n" (builtins.readFile ./__init__.py))
  );
  version = lib.removePrefix "__version__ = \"" (lib.removeSuffix "\"" versionLine);
in

buildPythonApplication {
  pname = "jackify";
  inherit version;
  
  src = ./.;
  
  format = "pyproject";
  
  nativeBuildInputs = [
    setuptools
    wheel
  ];
  
  propagatedBuildInputs = [
    pyside6
    psutil
    requests
    tqdm
    pycryptodome
    pyyaml
    vdf
    packaging
  ];
  
  # Don't run tests during build (no test suite yet)
  doCheck = false;
  
  meta = with lib; {
    description = "A tool for running Wabbajack modlists natively on Linux";
    homepage = "https://github.com/Omni-guides/Jackify";
    license = licenses.gpl3Plus;
    platforms = platforms.linux;
    mainProgram = "jackify";
  };
}
