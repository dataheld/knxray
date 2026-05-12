{
  description = "Diffable plain-text JSON from *.knxproj files via xknxproject";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.11";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-schemas.url = "github:DeterminateSystems/flake-schemas";
  };

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      flake-schemas,
      ...
    }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
      overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
      editableOverlay = workspace.mkEditablePyprojectOverlay { root = "$REPO_ROOT"; };

      pythonSets = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python3;
        in
        (pkgs.callPackage pyproject-nix.build.packages { inherit python; }).overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.wheel
            overlay
          ]
        )
      );
    in
    {
      schemas = flake-schemas.schemas;

      packages = forAllSystems (system: {
        default = pythonSets.${system}.mkVirtualEnv "knxplain-env" workspace.deps.default;
      });

      apps = forAllSystems (system: rec {
        knxshow = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/knxshow";
        };
        knxdiff = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/knxdiff";
        };
        default = knxshow;
      });

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system}.overrideScope editableOverlay;
          virtualenv = pythonSet.mkVirtualEnv "knxplain-dev-env" workspace.deps.all;
        in
        {
          default = pkgs.mkShell {
            packages = [ virtualenv uv2nix.packages.${system}.uv-bin ];
            env = {
              UV_NO_SYNC = "1";
              UV_PYTHON = pythonSet.python.interpreter;
              UV_PYTHON_DOWNLOADS = "never";
            };
            shellHook = ''
              unset PYTHONPATH
              export REPO_ROOT=$(git rev-parse --show-toplevel)
            '';
          };
        }
      );

      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          testVenv = pythonSets.${system}.mkVirtualEnv "knxplain-test-env" workspace.deps.all;
        in
        {
          pytest = pkgs.runCommand "knxplain-pytest" { nativeBuildInputs = [ testVenv ]; } ''
            export HOME=$(mktemp -d)
            pytest ${self}/tests -v --tb=short -p no:cacheprovider
            touch $out
          '';
        }
      );
    };
}
