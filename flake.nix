{
  description = "Diffable plain-text JSON from *.knxproj files via xknxproject";

  inputs = {
    nullkomma.url = "github:dataheld/nullkomma/c5379539f702e6d271f5291bca6a627f4fa557d3";
    nixpkgs.follows = "nullkomma/nixpkgs";
  };

  outputs =
    inputs:
    inputs.nullkomma.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      nullkomma = {
        gitignore = [ ".claude/" ];
        lint.markdown = {
          MD013 = false;
          MD033.allowed-elements = [ "img" ];
        };
        python.enable = true;
        quarto = {
          enable = true;
          root = ./docs;
          brand.enable = true;
        };
        cloudflare = {
          enable = true;
          domain = "maxheld.de";
        };
      };

      partitions.dev = {
        extraInputsFlake = ./dev;
        module =
          { inputs, ... }:
          {
            nullkomma.brand = inputs.brand;
          };
      };

      perSystem =
        { pkgs, ... }:
        {
          nullkomma.python.test.packages = [ pkgs.git ];
          nullkomma.editor.vscode.settings."files.associations"."*.ambr" = "json";
        };
    };
}
