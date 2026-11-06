{
  description = "Diffable plain-text JSON from *.knxproj files via xknxproject";

  inputs = {
    nullkomma.url = "github:dataheld/nullkomma/9c16eec10aae871240ac574b0158adb0ef961154";
    nixpkgs.follows = "nullkomma/nixpkgs";
  };

  outputs =
    inputs:
    inputs.nullkomma.lib.mkFlake { inherit inputs; } {
      nullkomma = {
        gitignore = [ ".claude/" ];
        lint.markdown = {
          MD013 = false;
          MD033.allowed-elements = [ "img" ];
        };
        python.enable = true;
        quarto = {
          enable = true;
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
