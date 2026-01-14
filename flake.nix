{
  description = "A tool for running Wabbajack modlists natively on Linux";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        jackify = pkgs.python3Packages.callPackage ./package.nix { };
        
      in {
        packages = {
          default = jackify;
          jackify = jackify;
        };
        
        apps = {
          default = {
            type = "app";
            program = "${jackify}/bin/jackify";
          };
        };
        
        devShells.default = pkgs.mkShell {
          inputsFrom = [ jackify ];
          
          buildInputs = with pkgs.python3Packages; [
            # Dev tools
            black
            flake8
            pytest
          ];
          
          shellHook = ''
            echo "Jackify development environment"
            echo "Run: python -m __main__ to start"
          '';
        };
      }
    );
}
