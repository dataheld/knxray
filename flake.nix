{
  description = "Diffable plain-text JSON from *.knxproj files via xknxproject";

  inputs = {
    nullkomma.url = "https://flakehub.com/f/dataheld/nullkomma/0.1.*";
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
        lint.markdown.MD033.allowed-elements = [ "img" ];
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
        { config, pkgs, ... }:
        {
          nullkomma.python.test.packages = [ pkgs.git ];
          nullkomma.editor.vscode.settings."files.associations"."*.ambr" = "json";
          checks.pytest = config.checks.python-test;
        };
    };
}
